import boto3
import json
import constant
import base64
import requests
from azdevops_client import AzDevOpsClient
from agent_manager import AgentManager

def get_ssm_parameter(parameter, decrypt=False):
    client = boto3.client('ssm')
    response = client.get_parameter(Name=parameter, WithDecryption=decrypt)
    
    return response['Parameter']['Value']

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('azdevops-ephemeral-agents')
    project_name="Spikes"

    azdevops_project_url = get_ssm_parameter('azdevops.url') + f'/{project_name}'
    azdevops_pat = get_ssm_parameter('azdevops.agentregistration.token', True)

    azdevops_client = AzDevOpsClient(azdevops_pat, 'jayytee', project_name)
    agent_manager = AgentManager(table, azdevops_client)
    the_environment = 'MyApp-Production'

    agent_manager.add_agent('i-123098u123', azdevops_project_url, the_environment)
    agent_manager.add_agent('i-123098u124', azdevops_project_url, the_environment)
    agent_manager.add_agent('i-123098u125', azdevops_project_url, the_environment)
    agent_manager.remove_agent('i-123098u125')

    agent_manager.remove_agent('i-055d39d6b8875ae7d')


