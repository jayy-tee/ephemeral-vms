# Automated registration/de-registration of ephemeral Azure Pipelines VM resources in AWS

## Scenario
This repo provides a solution addressing a scenario where a person/team:
* has an AWS environment, and
* uses Azure DevOps to build/deploy applications and infrastructure, and
* use YAML pipelines for deployment, with
* Virtual Machine resources registered to an Environment in Azure DevOps on first-launch, and
* Virtual Machine resources are removed from Azure DevOps when terminated

In the above scenario, the virtual machine resources are considered ephemeral, with EC2 instances managed using Autoscaling Groups in AWS.

## Deployment
A functional deployment is offered to demonstrate the solution. See [deploy/readme.md](deploy/readme.md) for full steps.

## Solution overview
### Components
* DynamoDb
* EC2 / Autoscaling
* Lambda (Python)
* S3
* SNS
* SSM

### Required Software
* Python 3.8
* Terraform

### Agent/VM registration
Userdata scripts are used to perform the initial registration against Azure DevOps at launch. EC2 instance tags are used to specify AzureDevOps project name, environment name etc.

Simultaneously, the Autoscaling Group is configured to publish to an SNS topic when instances are launched/terminated. A Lambda function is subscribed to the topic and persists data in a DynamoDb table (rationale captured in design decisions below).

### Agent/VM de-registration
When an instance is terminated, a notification is published to the SNS topic, triggering the Lambda function. The Lambda handler looks up the terminated instance in the DynamoDb table and optimistically removes it from the Environment in Azure DevOps.

## Design decisions
### DynamoDb/State table
A key factor influencing the architecture of this solution is the timing of the SNS notifications reaching the Lambda function. The initial design was stateless, relying only on EC2 instance tags. However, I've noticed a race condition in real world scenarios whereby tag data for a terminated instance is often removed from EC2 before Lambda is triggered. To address this, the tag values are enriched (with ID's from Azure DevOps) and persisted separately in DynamoDb at launch, removing the dependency on the tags for the re-registration process.

### Orchestration/Coupling
I have implemented this solution without coordinating events between Azure DevOps and AWS (using webhooks etc). I also elected not to couple launch scripts with the data stored in DynamoDb at registration. That is, the launch scripts are not aware of the overarching solution and focus only on registering themselves in Azure DevOps. As a result, it is possible for a registration to fail and still have data written to DynamoDb. The Lambda function treats this optimistically - it will attempt to delete the agent anyway.