import constant
import botocore

class Agent:
    def __init__(self, instance_id: str, azdevops_project_name: str, azdevops_environment_name: str, azdevops_environment_id: int):
        self.instance_id = instance_id
        self.azdevops_project_name = azdevops_project_name
        self.azdevops_environment_name = azdevops_environment_name
        self.azdevops_environment_id = azdevops_environment_id

class AgentManager():
    def __init__(self, dynamodb_table: object):
        self.dynamodb_table = dynamodb_table

    def add_agent(self, agent: object):
        self.dynamodb_table.put_item(Item = {
            constant.TABLE_PRIMARY_KEY: agent.instance_id,
            constant.AZP_PROJECT: agent.azdevops_project_name,
            constant.AZP_ENVIRONMENT_TAG: agent.azdevops_environment_name,
            constant.AZP_ENVIRONMENT_ID: agent.azdevops_environment_id,
        })

    def get_agent_by_id(self, instance_id: str):
        try:
            response = self.dynamodb_table.get_item(Key={constant.TABLE_PRIMARY_KEY: instance_id})
        except botocore.exceptions.ClientError as e:
            raise Exception(e.response['Error']['Message'])

        try:
            item = response['Item']
        except KeyError as e:
            print(f'No agent record found for instance {instance_id}')
            return
        
        return Agent(item[constant.TABLE_PRIMARY_KEY], item[constant.AZP_PROJECT], item[constant.AZP_ENVIRONMENT_TAG], item[constant.AZP_ENVIRONMENT_ID])

    def remove_agent_by_id(self, instance_id: str):
        try:
            self.dynamodb_table.delete_item(Key = {
                constant.TABLE_PRIMARY_KEY: instance_id
            })
        except botocore.exceptions.ClientError as e:
            raise Exception(e.response['Error']['Message'])