import boto3
import json
import constant
import base64
import requests


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

def get_azdevops_environment(environment_name, token, azp_project_url):
    token_b64 = base64.b64encode((token + ':').encode('ascii')).decode()
    headers = { 'Authorization': f'Basic {token_b64}' }
    url = f'{azp_project_url}/_apis/pipelines/environments/?api-version=6.1-preview.1&name={environment_name}'
    environments = requests.get(url, headers=headers).json()

    if (len(environments['value']) > 0):
        return environments['value'][0]


def remove_instance_from_pool(instance_id):
    azp_url = get_ssm_parameter('azdevops.url')
    azdevops_pat = get_ssm_parameter('azdevops.agentregistration.token', True)
    azdevops_pat_b64 = base64.b64encode((azdevops_pat + ':').encode('ascii')).decode()

    instance_tags = get_instance_tags(instance_id)
    environment_name = get_instance_environment_tag(instance_tags)
    project_name = get_instance_devopsproject(instance_tags)

    print(f'Get Agent Environment ID for Instance {instance_id} in Project {project_name}')
    environment = get_azdevops_environment(environment_name, azdevops_pat, f'{azp_url}/{project_name}')

    if (environment == None):
        print("No agent pool found")
        return

    environment_id = environment['id']

    print(f"Get Agent ID in Environment {environment['id']}")
    headers = { 'Authorization': f'Basic {azdevops_pat_b64}' }
    agents_url = f'{azp_url}/{project_name}/_apis/pipelines/environments/{environment_id}/providers/virtualmachines/?api-version=6.1-preview.1&name={instance_id}'
    print(agents_url)
    agents = requests.get(agents_url, headers=headers).json()

    print(agents['count'])
    if (agents['count'] > 0):
        agent_id = agents['value'][0]['id']
        delete_url = f'{azp_url}/{project_name}/_apis/pipelines/environments/{environment_id}/providers/virtualmachines/{agent_id}?api-version=6.1-preview.1'

        print(f'Deleting.... {delete_url}')
        delete = requests.delete(delete_url, headers=headers)
        if (delete.status_code < 200 and delete.status_code > 299):
            print(f'Failed to delete agent. AzDevOps Status: {delete.status_code})')


def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        print(message)
        message_instance = message['EC2InstanceId']
        print(f'EC2 Instance {message_instance} was terminated')
        remove_instance_from_pool(message_instance)
    
    