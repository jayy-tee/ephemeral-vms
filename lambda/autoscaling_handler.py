import boto3
import constant
from azdevops_client import AzDevOpsClient
from agent_manager import AgentManager

def get_ssm_parameter(parameter, decrypt=False):
    client = boto3.client('ssm')
    response = client.get_parameter(Name=parameter, WithDecryption=decrypt)
    
    return response['Parameter']['Value']

def get_instance_tags(instance_id):
    ec2_client = boto3.client('ec2')
    instance_tags = ec2_client.describe_tags(
        Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])

    return(instance_tags)

def get_instance_environment_tag(instance_tags):
    tags = [x for x in instance_tags['Tags'] if x['Key'] == constant.AZP_ENVIRONMENT_TAG ]
    
    if (len(tags) > 0):
        return tags[0]['Value']

def get_instance_devopsproject(instance_tags):
    projects = [x for x in instance_tags['Tags'] if x['Key'] == constant.AZP_PROJECT ]
    
    if (len(projects) > 0):
        return projects[0]['Value']

def get_azdevops_tags_from_instance(instance_id: str):
    raise NotImplementedError

def register_instance(instance_id: int):
    raise NotImplementedError

class SsmClient:
    def __init__(self):
        self.client = boto3.client('ssm')

    def get_parameter(self, parameter, decrypt=False):
        response = self.client.get_parameter(Name=parameter, WithDecryption=decrypt)
        
        return response['Parameter']['Value']

def lambda_handler(event, context):
    ssm_client = SsmClient()
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('azdevops-ephemeral-agents')

    azdevops_org_url = ssm_client.get_parameter('azdevops.url')
    azdevops_pat = ssm_client.get_parameter('azdevops.agentregistration.token', True)
    azdevops_client = AzDevOpsClient(azdevops_pat, azdevops_org_url, None)

    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        instance_id = message['EC2InstanceId']

        if (message['Event'] == 'autoscaling:EC2_INSTANCE_LAUNCH'):
            register_instance(instance_id)
        elif (message['Event'] == 'autoscaling:EC2_INSTANCE_TERMINATE'):
            agent_manager = AgentManager(table, azdevops_client)

    
    