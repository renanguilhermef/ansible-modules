##
# Entrocim projecs module, return projects from host according with state (local,replica or all) - Ansible module
#!/usr/bin/python3
##
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


def main():
    module = AnsibleModule(
        argument_spec = dict(
           entrocim_hostname = dict(required=True, type='str'),
           entrocim_project_type=dict(default='all',type='str',choices=['all','local','replica'])
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    projs = h.eval("projs()")
    list_proj = []
    project_type = module.params['entrocim_project_type']
    if project_type == 'local':
        for proj in projs:
            if proj['type'] == 'local': 
                list_proj.append(proj['name'])
    elif project_type == 'replica':
        for proj in projs:
            if proj['type'] == 'replica': 
                list_proj.append(proj['name'])
    else:
        for proj in projs:
            list_proj.append(proj['name'])
            
    module.exit_json(changed=False, list=list_proj)

if __name__ == '__main__':
    main()