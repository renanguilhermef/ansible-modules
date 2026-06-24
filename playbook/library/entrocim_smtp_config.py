##
# Entrocim update ldap - Ansible module
#!/usr/bin/python3
##
import hszinc
from ansible.module_utils.basic import *
import ansible.module_utils.hvacDell as hvacDell
import ansible.module_utils.haystackDell as haystack
from cryptography.fernet import Fernet
import yaml

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

def addSMTPConfiguration(h,uri, _from):
        
    result = h.eval("hostSettings(\"email\")").metadata['rec']

    tls = False
    uri = uri
    From = _from
    password = '{}'
    username = ""
    mod = result['mod']
    
    commit_grid = hszinc.Grid()
    commit_grid.column['id'] = {}
    commit_grid.column['tls'] = {}
    commit_grid.column['uri'] = {}
    commit_grid.column['from'] = {}
    commit_grid.column['password'] = {}
    commit_grid.column['sysMod'] = {}
    commit_grid.column['username'] = {}
    commit_grid.column['mod'] = {}
    
    commit_grid.append({"id": hszinc.Ref('h:email', value='"h:email"'), 
                        "tls": tls, 
                        "uri": hszinc.Uri(uri), 
                        "from": From, 
                        "password": password, 
                        "sysMod": hszinc.MARKER, 
                        "username": username, 
                        "mod": mod})
    
    h.call("hostCommit",commit_grid)

def main():
    module = AnsibleModule(
        argument_spec = dict(
           entrocim_hostname = dict(required=True, type='str'),
           entrocim_smtp_uri = dict(required=True, type='str'),
           entrocim_smtp_from = dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    
    try:
        addSMTPConfiguration(h,module.params['entrocim_smtp_uri'], module.params['entrocim_smtp_from'])
        module.exit_json(changed=False, stdout="Configuration was a success")
    except Exception as err:
        module.fail_json(msg="Configuration failed with error " + str(err))
 
if __name__ == '__main__':
    main()