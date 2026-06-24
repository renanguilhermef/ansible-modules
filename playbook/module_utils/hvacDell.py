# This module is used to connect on the dell hashicorp 
# Class hvacEMS to get secret from EMS namespace on dell hashicorp
import hvac 
import urllib3

class hvacProd:

    def __init__(self,vault_namespace,vault_role_id,vault_secret_id):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.vault_addr = "https://vault.dell.com"
        self.vault_namespace = vault_namespace
        self.vault_role_id = vault_role_id
        self.vault_secret_id = vault_secret_id
        self.client = hvac.Client(url=self.vault_addr, namespace=self.vault_namespace, verify=False)
        self.client.auth.approle.login(role_id=self.vault_role_id, secret_id=self.vault_secret_id, use_token=True)
    
    def getKeyValue(self,secret_path,key):
        mount_point, path = secret_path.split('/', 1)
        read_response = self.client.secrets.kv.v1.read_secret(mount_point=mount_point, path=path)
        return read_response['data']['data'][key]

