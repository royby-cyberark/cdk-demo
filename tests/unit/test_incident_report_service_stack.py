import aws_cdk as core
import aws_cdk.assertions as assertions

from incident_report_service.incident_report_service_stack import IncidentReportServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in incident_report_service/incident_report_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = IncidentReportServiceStack(app, "incident-report-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
