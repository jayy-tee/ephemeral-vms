import constant
import botocore

class AgentManager():
    def __init__(self, dynamodb_table: object, azdevops_client: object):
        self.azdevops_client = azdevops_client
        self.dynamodb_table = dynamodb_table

    def add_agent(self, instance_id: str, project_name: str, environment_name: str):
        azdevops_environment = self.azdevops_client.get_environment(environment_name)
        azdevops_environment_url = self.azdevops_client.get_url_for_environment(azdevops_environment['id'])

        self.dynamodb_table.put_item(Item = {
            constant.TABLE_PRIMARY_KEY: instance_id,
            constant.AZP_PROJECT: project_name,
            constant.AZP_ENVIRONMENT_TAG: environment_name,
            constant.AZP_ENVIRONMENT_ID: azdevops_environment['id'],
        })
    
    def remove_agent(self, instance_id: str):
        # get item from table
        try:
            response = self.dynamodb_table.get_item(Key={constant.TABLE_PRIMARY_KEY: instance_id})
        except botocore.exceptions.ClientError as e:
            raise Exception(e.response['Error']['Message'])

        try:
            environment_id = response['Item'][constant.AZP_ENVIRONMENT_ID]
        except KeyError as e:
            print(f'No agent found for instance {instance_id}')
            return

        self.azdevops_client.delete_virtualmachine_from_environment(environment_id, instance_id)
        self.dynamodb_table.delete_item(Key = {
            constant.TABLE_PRIMARY_KEY: instance_id
        })