##
# Entrocim crypto config - Ansible module
#!/usr/bin/python3
##
import hszinc
import ansible.module_utils.hvacDell as hvacDell
import ansible.module_utils.haystackDell as haystack
from cryptography.fernet import Fernet
import yaml
from ansible.module_utils.basic import *

def openHaystackConnection(hostname,project): 
    
    #open key to decrypt vault_params file
    with open("library/parameters/filekey.key", 'rb') as filekey:
        fernet = Fernet(filekey.read())

    #read file encrypted
    with open("library/parameters/haystack_hvac.yml", 'rb') as enc_file:
        encrypted = enc_file.read()

    #decrypt file and load yaml file
    params = yaml.full_load(fernet.decrypt(encrypted))

    h = hvacDell.hvacProd(params["vault_namespace"],params["vault_role_id"],params["vault_secret_id"])

    hvac_secret_path = "/kv/data/SERVICE_ACCOUNT/api_user"
    hvac_key_username = h.getKeyValue(hvac_secret_path,"username")
    hvac_key_pass =  h.getKeyValue(hvac_secret_path,"password")

    
    return(haystack.haystackEMS(hostname,project,hvac_key_username,hvac_key_pass))

def addCryptoTrustUri(h,uri,alias):
    commit_grid = hszinc.Grid()
    commit_grid.column["uri"] = {}
    commit_grid.column["alias"] = {}
    commit_grid.append({"uri": hszinc.Uri(uri),"alias": alias})
    op = h.call("cryptoTrustUri",commit_grid)
    return op

def main():
    module = AnsibleModule(
        argument_spec = dict(
           entrocim_crypto_uri = dict(required=True, type='str'),
           entrocim_crypto_alias= dict(required=True, type='str'),
           entrocim_hostname = dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    result = addCryptoTrustUri(h,module.params['entrocim_crypto_uri'],module.params['entrocim_crypto_alias'])
    if "ArgErr" in result: 
        module.fail_json(msg=result)
    else: 
        module.exit_json(changed=False, stdout="Crypto configuration success")

if __name__ == '__main__':
    main()