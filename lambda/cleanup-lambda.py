import boto3
import json
import constant
import base64
import requests


def get_instance_tags(instance_id):
    ec2_client = boto3.client('ec2')
    instance_tags = ec2_client.describe_tags(
        Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])

    return(instance_tags)

def get_instance_agentpool(instance_tags):
    agent_pools = [x for x in instance_tags['Tags'] if x['Key'] == constant.AGENTPOOL_TAGNAME ]
    
    if (len(agent_pools) > 0):
        return agent_pools[0]['Value']

def get_instance_devopsproject(instance_tags):
    projects = [x for x in instance_tags['Tags'] if x['Key'] == constant.AZP_PROJECT ]
    
    if (len(projects) > 0):
        return projects[0]['Value']


def remove_instance_from_pool(instance_id):
    azdevops_pat = 'ap5ocillfloerwz6e6ondwtrsldyt5r5nhf4trfgyg7mvxtzosbq'
    azdevops_pat_b64 = base64.b64encode((azdevops_pat + ':').encode('ascii')).decode()

    instance_tags = get_instance_tags(instance_id)
    agent_pool = get_instance_agentpool(instance_tags)
    project_name = get_instance_devopsproject(instance_tags)

    print(f'Get Agent Pool ID for Instance {instance_id} in Project {project_name}')

    if (agent_pool == None):
        print("No agent pool found")
        return

    print(f"Get Agent ID in pool {agent_pool}")
    headers = { 'Authorization': f'Basic {azdevops_pat_b64}' }
    agents_url = f'{constant.AZP_URL}/{project_name}/_apis/pipelines/environments/{agent_pool}/providers/virtualmachines/?api-version=6.1-preview.1&name={instance_id}'
    print(agents_url)
    agents = requests.get(agents_url, headers=headers).json()

    print(agents['count'])
    if (agents['count'] > 0):
        agent_id = agents['value'][0]['id']
        delete_url = f'{constant.AZP_URL}/{project_name}/_apis/pipelines/environments/{agent_pool}/providers/virtualmachines/{agent_id}?api-version=6.1-preview.1'

        print(f'Deleting.... {delete_url}')
        delete = requests.delete(delete_url, headers=headers)


def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        print(message)
        message_instance = message['EC2InstanceId']
        print(f'EC2 Instance {message_instance} was terminated')
        remove_instance_from_pool(message_instance)
    
    