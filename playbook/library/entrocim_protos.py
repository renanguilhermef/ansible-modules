##
# Entrocim protos - Ansible module
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


def addProtosConfiguration(h,dis,userProtoName,userRole,ldapUserProtoAttrVal,projects):

        dis = dis 
        userProto = hszinc.MARKER
        userProtoName = userProtoName
        userRole = userRole 
        ldapUserProtoAttrVal = ldapUserProtoAttrVal 
        for project in projects: 
            if project == projects[0]:
                projAccessFilter = "name == \""+ project + "\"" 
            else: 
                projAccessFilter = projAccessFilter + " or name == \""+ project + "\""

        commit_grid = hszinc.Grid()
        commit_grid.column['dis'] = {}
        commit_grid.column['userProto'] = {}
        commit_grid.column['userProtoName'] = {}
        commit_grid.column['userRole'] = {}
        commit_grid.column['ldapUserProtoAttrVal'] = {}
        commit_grid.column['projAccessFilter'] = {}

        commit_grid.append({"dis": dis,
                            "userProto": userProto,
                            "userProtoName":userProtoName,
                            "userRole": userRole,
                            "ldapUserProtoAttrVal": ldapUserProtoAttrVal,
                            "projAccessFilter": projAccessFilter})

        h.call("userProtoNew",commit_grid)

def updateArcWriteAccess(h):

    getProtos = h.eval("userProtoReadAll(userProto, { search:\"\" })")

    for proto in getProtos:
        if proto["userRole"] == 'op':
            commit_grid = hszinc.Grid()
            commit_grid.column['id'] = {}
            commit_grid.column['arcWriteAccess'] = {}
            commit_grid.column['mod'] = {}
            commit_grid.append({"id": proto["id"],
                                "arcWriteAccess": "new, edit, move, remove, newPart, editPart",
                                "mod": proto['mod']})
                                
            h.call("userProtoEdit",commit_grid)

def main():
    module = AnsibleModule(
        argument_spec = dict(
           entrocim_hostname = dict(required=True, type='str'),
           entrocim_proto_dis = dict(required=False, type='str'),
           entrocim_proto_name = dict(required=False, type='str'),
           entrocim_proto_role = dict(required=False, type='str'),
           entrocim_proto_ldap = dict(required=False, type='str'),
           entrocim_proto_project = dict(required=False, type='str'),
           entrocim_proto_state = dict(default='add',type='str', choices=['add','updateArcWriteAccess'])
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    state = module.params['entrocim_proto_state']
    if module.params['entrocim_proto_project'] != None: 
         projs = list(module.params['entrocim_proto_project'].split(","))
    try:
        if state == "add":
            addProtosConfiguration(h,module.params['entrocim_proto_dis'],module.params['entrocim_proto_name'],
                                    module.params['entrocim_proto_role'],module.params['entrocim_proto_ldap'],projs)
            updateArcWriteAccess(h)##update write access
            module.exit_json(changed=True, stdout="Proto created")
        elif state == "updateArcWriteAccess":
            updateArcWriteAccess(h)
            module.exit_json(changed=True, stdout="ArcWriteAccess update for the operator users")
        else:
            module.fail_json(msg="Incorret state option")
       
    except Exception as err:
        module.fail_json(msg="Proto Creation failed: " + err)
  
if __name__ == '__main__':
    main()