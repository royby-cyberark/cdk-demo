#!/usr/bin/env python3
import os

import aws_cdk as cdk

from incident_report_service.incident_report_service_stack import IncidentReportServiceStack


app = cdk.App()
IncidentReportServiceStack(app, "IncidentReportServiceStack")

app.synth()
