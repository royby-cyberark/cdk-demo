from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_apigateway as api_gateway,
    aws_lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_lambda_python_alpha as lambda_python,
    aws_sns as sns,
    aws_sns_subscriptions as sns_sub,
    aws_sqs as sqs,
    CfnOutput,
    RemovalPolicy,
    Stack,
)
from constructs import Construct

PROD = False

class IncidentReportServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        incidents_table = dynamodb.Table(
            self,
            id='IncidentsTable',
            partition_key=dynamodb.Attribute(name='incident_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN if PROD else RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
        )

        rest_api = api_gateway.RestApi(
            self,
            'IncidentReportServiceApi',
            rest_api_name='Incident Reporting Service Rest API',
        )  

        incident_handler_lambda_role = iam.Role(
            scope=self,
            id='IncidentHandlerRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description='Optionally add description',
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')],
            # inline_policies=iam.Policy(),
        )

        incident_received_queue = sqs.Queue(
            self, "IncidentReceived",
        )        

        incident_handler_lambda = lambda_python.PythonFunction(
            self, 
            'IncidentHandlerLambda',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            entry='service',
            index='incident_event_lambda/handler.py',
            handler='lambda_handler',
            role=incident_handler_lambda_role,
            environment={
                'INCIDENTS_TABLE': incidents_table.table_name,
                'NOTIFICATIONS_QUEUE_URL': incident_received_queue.queue_url
            }
        )

        incidents_table.grant_read_write_data(incident_handler_lambda)        
        incident_received_queue.grant_send_messages(incident_handler_lambda)

        incident_response_resource = rest_api.root.add_resource('incidentReport')
        
        incident_response_resource.add_method(
            http_method='Post',
            integration=api_gateway.LambdaIntegration(incident_handler_lambda),
            # authorization_type=apigw.AuthorizationType.IAM,
        )

        incident_notifier_lambda_role = iam.Role(
            scope=self,
            id='IncidentNotifierRole',
            # role_name='IncidentNotifierRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            description='Optionally add description',
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')],
            # inline_policies=inline_policies,
        )        

        incidents_sns_topic = sns.Topic(self, 'IncidentReceivedTopic')
        incidents_sns_topic.add_subscription(sns_sub.EmailSubscription(email_address='roybjca@gmail.com'))

        incident_notifier_lambda = lambda_python.PythonFunction(
            self, 
            'IncidentNotifierLambda',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            entry='service',
            index='incident_notifier_lambda/handler.py',
            handler='lambda_handler',
            role=incident_notifier_lambda_role,
            environment={
                'INCIDENT_NOTIFICATION_SNS_TOPIC': incidents_sns_topic.topic_arn
            }
        )

        incidents_sns_topic.grant_publish(incident_notifier_lambda)
        incident_received_queue.grant_consume_messages(incident_notifier_lambda)

        incident_notifier_lambda.add_event_source(lambda_event_sources.SqsEventSource(queue=incident_received_queue))
