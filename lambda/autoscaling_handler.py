import boto3
import constant
import json
import os
from azdevops_client import AzDevOpsClient
from agent_manager import Agent, AgentManager

class SsmClient:
    def __init__(self):
        self.client = boto3.client('ssm')

    def get_parameter(self, parameter, decrypt=False):
        response = self.client.get_parameter(Name=parameter, WithDecryption=decrypt)
        
        return response['Parameter']['Value']

table_name = os.environ['AGENT_TABLE_NAME'] or 'azdevops-ephemeral-agents'
ssm_client = SsmClient()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
agent_manager = AgentManager(table)

azdevops_org_url = ssm_client.get_parameter('azdevops.url')
azdevops_pat = ssm_client.get_parameter('azdevops.agentregistration.token', True)
azdevops_client = AzDevOpsClient(azdevops_pat, azdevops_org_url, None)

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

def get_azdevops_data_from_instance(instance_id: str):
    tags = get_instance_tags(instance_id)
    return {
        'Environment': get_instance_environment_tag(tags),
        'Project': get_instance_devopsproject(tags)
    }

def register_instance(instance_id: str):
    instance_data = get_azdevops_data_from_instance(instance_id)
    azdevops_client.set_project(instance_data['Project'])

    environment = azdevops_client.get_environment(instance_data['Environment'])
    agent = Agent(instance_id, instance_data['Project'], instance_data['Environment'], environment['id'])

    agent_manager.add_agent(agent)

def remove_instance(instance_id: str):
    agent = agent_manager.get_agent_by_id(instance_id)

    if (agent == None):
        return
    
    azdevops_client.set_project(agent.azdevops_project_name)
    azdevops_client.delete_virtualmachine_from_environment(agent.azdevops_environment_id, agent.instance_id)
    agent_manager.remove_agent_by_id(agent.instance_id)

def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        instance_id = message['EC2InstanceId']

        if (message['Event'] == 'autoscaling:EC2_INSTANCE_LAUNCH'):
            register_instance(instance_id)
        elif (message['Event'] == 'autoscaling:EC2_INSTANCE_TERMINATE'):
            remove_instance(instance_id)
        else:
            pass