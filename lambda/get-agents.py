from azdevops_client import AzDevOpsClient
import boto3

def get_ssm_parameter(parameter, decrypt=False):
    client = boto3.client('ssm')
    response = client.get_parameter(Name=parameter, WithDecryption=decrypt)
    
    return response['Parameter']['Value']

if __name__ == '__main__':
    project_name="Spikes"

    azdevops_pat = get_ssm_parameter('azdevops.agentregistration.token', True)
    azdevops_client = AzDevOpsClient(azdevops_pat, 'jayytee', project_name)

    print(azdevops_client.get_agent_packages())