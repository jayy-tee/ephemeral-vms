# Deployment Steps

## Pre-requisite steps
### Azure DevOps
We assume you have an Azure DevOps Organization with at least one "Environment" configured.

You will need to create a Personal Access Token (PAT) with the following permissions:
* Agent Pools (Read & manage)
* Build (Read)
* Deployment Groups (Read & manage)
* Environment (Read & manage)
* Task Groups (Read, create * manage)

### Build/prepare dependent resources for the Lambda stack
You will need to first build (prepare a zip file) for the Lambda function and ec2-scripts folder. 
```
[you@yourhost deploy]$ bash build-and-prepare-artifacts.sh
```

## Deploy Lambda Stack
The `lambda-stack` terraform module deploys the following:
* DynamoDb Table
* Lambda function (and IAM Roles, Log Groups and so forth)
* S3 Buckets (EC2 Launch Scripts and Lambda deployment)
* SNS Topic
* SSM Parameters

You will need to modify [`lambda-stack/terraform.tfvars`](lambda-stack/terraform.tfvars) file with your own values.
Hint: You will need to add the following:
```
azdevops_url = "https://dev.azure.com/yourorganization"
azdevops_pat = "your-personal-access-token-value"
```

Deploy:
```
[you@yourhost lambda-stack]$ terraform apply
```

The output of the `lambda-stack` module can be captured and included for inclusion in `example-app-stack`:
```
[you@yourhost lambda-stack]$ terraform output > ../example-app-stack/deps.auto.tfvars
```

## Deploy Example EC2 app stack
The `example-app-stack` terraform module deploys the following:
* EC2 Autoscaling Group
* EC2 IAM Role(s)
* EC2 Launch Template
* Security Group
* VPC

As before, you will need to modify [`example-app-stack/terraform.tfvars`](example-app-stack/terraform.tfvars) file with your own values.

Deploy:
```
[you@yourhost example-app-stack]$ terraform apply
```

Once the stack is deployed, you should be able to add instances to the Autoscaling Group and have them appear in the specified Azure DevOps Environment. Likewise, when the instances are scaled down, they should be automatically removed from Azure DevOps.