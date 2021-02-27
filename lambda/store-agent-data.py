import boto3
import json
import constant
import base64
import requests
from azdevops_client import AzDevOpsClient

TABLE_PRIMARY_KEY = 'Instance-Id'

class AgentManager():
    def __init__(self, dynamodb_table: object, azdevops_client: object):
        self.azdevops_client = azdevops_client
        self.dynamodb_table = dynamodb_table

    def add_agent(self, instance_id: str, project_name: str, environment_name: str):
        azdevops_environment = self.azdevops_client.get_environment(environment_name)
        azdevops_environment_url = self.azdevops_client.get_url_for_environment(azdevops_environment['id'])

        self.dynamodb_table.put_item(Item = {
            TABLE_PRIMARY_KEY: instance_id,
            constant.AZP_PROJECT: project_name,
            constant.AZP_ENVIRONMENT_TAG: environment_name,
            constant.AZP_ENVIRONMENT_ID: azdevops_environment['id'],
        })
    
    def remove_agent(self, instance_id: str):
        # get item from table
        try:
            response = table.get_item(Key={TABLE_PRIMARY_KEY: instance_id})
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])

        try:
            environment_id = response['Item'][constant.AZP_ENVIRONMENT_ID]
        except KeyError as e:
            print(f'No agent found for instance {instance_id}')
            return

        azdevops_client.delete_virtualmachine_from_environment(environment_id, instance_id)
        table.delete_item(Key = {
            TABLE_PRIMARY_KEY: instance_id
        })

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

    azdevops_client = AzDevOpsClient(azdevops_pat, azdevops_project_url)
    agent_manager = AgentManager(table, azdevops_client)
    the_environment = 'MyApp-Production'

    agent_manager.add_agent('i-123098u123', azdevops_project_url, the_environment)
    agent_manager.add_agent('i-123098u124', azdevops_project_url, the_environment)
    agent_manager.add_agent('i-123098u125', azdevops_project_url, the_environment)
    agent_manager.remove_agent('i-123098u125')

    agent_manager.remove_agent('i-123098u1225')


