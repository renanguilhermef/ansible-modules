##
# Entrocim sysmod config - Ansible module
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
           entrocim_sysmod_name= dict(required=True, type='str'),
           entrocim_hostname = dict(required=True, type='str'),
           entrocim_sysmod_state=dict(default='add',type='str', choices=['add','remove'])
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    state = module.params['entrocim_sysmod_state']
    if state == "add":
        result = h.eval("sysModAdd([\"" + module.params['entrocim_sysmod_name'] + "\"])")
    elif state == "remove": 
        result = h.eval("sysModRemove([\"" + module.params['entrocim_sysmod_name'] + "\"])")
    else:
        module.fail_json(msg="State option invalid " + module.params["entrocim_sysmod_state"] )

    if "err" in result: 
        module.fail_json(msg=result)
    else: 
        module.exit_json(changed=False, stdout="SysMod" + module.params["entrocim_sysmod_name"] + " enabled")

if __name__ == '__main__':
    main()