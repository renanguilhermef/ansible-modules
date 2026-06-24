##
# Entrocim crypto extension config - Ansible module
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
           entrocim_license=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    
    try:
        h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
        h.eval("licInstall(\"" + module.params['entrocim_license'].replace("\n", "\\n") + "\")")
        h.eval("licUpdate()")
        module.exit_json(changed=False, stdout="License updated")
    except Exception as err:
        module.fail_json(msg="License failed with error " + str(err))

if __name__ == '__main__':
    main()