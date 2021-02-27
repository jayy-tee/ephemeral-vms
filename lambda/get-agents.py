from azdevops_client import AzDevOpsClient
from agent_manager import Agent, AgentManager
import json
import boto3

def get_ssm_parameter(parameter, decrypt=False):
    client = boto3.client('ssm')
    response = client.get_parameter(Name=parameter, WithDecryption=decrypt)
    
    return response['Parameter']['Value']

if __name__ == '__main__':
    # project_name="Spikes"

    # azdevops_pat = get_ssm_parameter('azdevops.agentregistration.token', True)
    # azdevops_client = AzDevOpsClient(azdevops_pat, 'jayytee', project_name)

    # print(azdevops_client.get_agent_packages())

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('azdevops-ephemeral-agents')

    agent_manager = AgentManager(table)

    agent = agent_manager.get_agent_by_id('i-123098u124')
    print(agent.__dict__)
