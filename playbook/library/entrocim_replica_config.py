##
# Entrocim replica config - Ansible module
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


module = AnsibleModule(
    argument_spec=dict(
        hostname=dict(required=True, type='str'),
        config=dict(required=True, type='str'),
        id=dict(required=True, type='str')
    ),
    supports_check_mode=True
)


def check_exit(result):
    if "fail" in str(result):
        module.fail_json(msg="Replica config failed: " + str(result))


def replicaCreate(hostname, id):
    h = openHaystackConnection(hostname,'sys')
    result = h.eval("projReplicate([@p:" + id + "])")
    check_exit(result)


def _replicaConf(h, id):
    commit_grid = hszinc.Grid()
    commit_grid.column['id'] = {}
    commit_grid.column['autoSync'] = {}
    commit_grid.append({"id": hszinc.Ref("p:"+id), "autoSync": hszinc.MARKER})
    return h.call("replicaConfig", commit_grid)


def replicaSetAndSync(hostname, id):
    h = openHaystackConnection(hostname,'sys')
    result = h.eval("replicaMode([@p:" + id + "], \"live\")")
    check_exit(result)
    result = h.eval("replicaSync([@p:" + id + "])")
    check_exit(result)
    result = _replicaConf(h, id)
    check_exit(result)

def replicaGetInfo(hostname, id):
    h = openHaystackConnection(hostname,'sys')
    replica_info = h.eval("replicas().find(r => r->id == " + str(hszinc.Ref("p:"+id)) + ") ")
    #format dict values to string for do not have issues when return to ansible 
    result = dict() 
    for key,value in list(replica_info[0].items()):
        result[key] = str(value)
    return result 

def main():
    if "create" in module.params["config"]:
        replicaCreate(module.params['hostname'], module.params['id'])
    elif "sync" in module.params["config"]:
        replicaSetAndSync(module.params['hostname'], module.params['id'])
    elif "get" in module.params['config']:
        #synchronize replica before to get replica details
        replicaSetAndSync(module.params['hostname'], module.params['id'])
        module.exit_json(changed=True, dict=replicaGetInfo(module.params['hostname'], module.params['id']))
        return 
    else:
        module.exit_json(
            changed=False, stdout="Invalid replica config provided: " + module.params["config"])
        return

    module.exit_json(changed=True, stdout="Replica Config Success")


if __name__ == '__main__':
    main()
