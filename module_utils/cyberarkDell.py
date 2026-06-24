# This module is used to connect on the dell cyberark 
# Class myvault to get secret password from service accounts dynamically

import urllib.parse                     # internal package for url encoding
import requests                         # requests package for REST interaction
import urllib3

class myvault:

    def __init__(self,vault_hid,vault_authn,secret):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.vault_url = "https://api.myvault.dell.com"
        self.vault_namespace = "MYVAULT" 
        self.vault_hid = vault_hid 
        self.vault_authn = vault_authn
        self.secret = secret

    def openAPIConnection(self):
        self.api_uri = self.vault_url + "/authn/" + self.vault_namespace  + "/" + urllib.parse.quote_plus(self.vault_hid) + "/authenticate"
        head = { 'Accept-Encoding': 'base64',
            'Content-Type': 'text/plain' }

        return requests.post(self.api_uri, data=self.vault_authn, verify=False, headers=head)

    def getPassword(self):
        response= self.openAPIConnection() 
        if (response.status_code == 200):
            token = response.text
            token_head = 'Token token="' + token + '"'
            self.api_uri = self.vault_url + "/secrets/" + self.vault_namespace + "/variable/" + urllib.parse.quote_plus(self.secret)
            head = { 'Authorization': token_head }
            response = requests.get(self.api_uri, verify=False, headers=head)
            if (response.status_code == 200):
                return response.text
            else:
                return False
        else:
            return False

