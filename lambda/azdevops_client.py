import base64
import json
import requests

class AzDevOpsClient:
    def __init__(self, access_token: str, organization_url: str, project_name: str):
        self.access_token = access_token
        self.azdevops_base_url = organization_url
        self.project_base_url = f'{self.azdevops_base_url}/{project_name}'
        self.token_b64 = base64.b64encode((self.access_token + ':').encode('ascii')).decode()
        self.request_headers = { 'Authorization': f'Basic {self.token_b64}', 'Accept': 'application/json' }

    def __invoke_get_request(self, url: str):
        response = requests.get(url, headers=self.request_headers)
        requests.request
        
        if (response.status_code > 299 and (response.headers.__contains__('Content-Type') and response.headers['Content-Type'] == 'application/json')):
            response.encoding = 'utf-8-sig'
            error = json.loads(response.text)
            raise Exception(error['message'])
        elif (response.status_code > 299):
            raise Exception(f'Request failed with status code {response.status_code}' )

        return response.json()
    
    def __invoke_delete_request(self, url: str):
        response = requests.delete(url, headers=self.request_headers)
        requests.request
        
        if (response.status_code > 299 and (response.headers.__contains__('Content-Type') and response.headers['Content-Type'] == 'application/json')):
            response.encoding = 'utf-8-sig'
            error = json.loads(response.text)
            raise Exception(error['message'])
        elif (response.status_code > 299):
            raise Exception(f'Request failed with status code {response.status_code}' )

        return
    
    def set_project(self, project_name: str):
        self.project_base_url = f'{self.azdevops_base_url}/{project_name}'


    def get_agent_packages(self):
        url = f'{self.azdevops_base_url}/_apis/distributedtask/packages/agent'
        return self.__invoke_get_request(url)

    def get_environment(self, environment_name):
        url = f'{self.project_base_url}/_apis/pipelines/environments/?api-version=6.1-preview.1&name={environment_name}'
        environments = self.__invoke_get_request(url)

        if (len(environments['value']) == 0):
            return
        
        return environments['value'][0]

    def get_url_for_environment(self, environment_id: int):
        url = f'{self.project_base_url}/_apis/pipelines/environments/{environment_id}'

        return url
    
    def get_environment_virtualmachines(self, environment_id: int):
        url = f'{self.project_base_url}/_apis/pipelines/environments/{environment_id}/providers/virtualmachines/?api-version=6.1-preview.1'

        return self.__invoke_get_request(url)

    def get_environment_virtualmachines(self, environment_id: int):
        environment_url = self.get_url_for_environment(environment_id)
        url = f'{environment_url}/providers/virtualmachines/?api-version=6.1-preview.1'

        return self.__invoke_get_request(url)

    def find_environment_virtualmachine(self, environment_id: int, name: str):
        environment_url = self.get_url_for_environment(environment_id)
        url = f'{environment_url}/providers/virtualmachines/?api-version=6.1-preview.1&name={name}'

        return self.__invoke_get_request(url)

    def delete_virtualmachine_from_environment(self, environment_id: int, name: str):
        environment_url = self.get_url_for_environment(environment_id)
        virtual_machines = self.find_environment_virtualmachine(environment_id, name)
           
        if (virtual_machines['count'] == 0):
            return
            
        virtual_machine_id = virtual_machines['value'][0]['id']
        delete_url = f'{environment_url}/providers/virtualmachines/{virtual_machine_id}?api-version=6.1-preview.1'

        self.__invoke_delete_request(delete_url)


        