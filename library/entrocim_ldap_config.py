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



def addLDAPConfiguration(h,host,port,userAttrs,userBaseDN,password,userProtoAttr,
                           serviceAccountDN,userProtoPriority,loginAttr):

        result = h.eval("hostSettings(\"ldap\").removeCol(\"is\")").metadata['rec']

        id = hszinc.Ref('h:ldap', value='"h:ldap"')
        tls = True
        host = host
        port = port
        userAttrs = userAttrs
        userBaseDN = userBaseDN
        password = password
        userProtoAttr = userProtoAttr
        loginUpdateMode = "updateOnLogin"
        userProtoDefault = ""
        serviceAccountDN = serviceAccountDN
        userProtoPriority = userProtoPriority
        loginAttr = loginAttr
        applyTagsFunc = ""
        connectTimeout = 1
        sysMod = result['sysMod']
        readTimeout = 10
        mod = result['mod']

        commit_grid = hszinc.Grid()
        commit_grid.column['id'] = {}
        commit_grid.column['tls'] = {}
        commit_grid.column['host'] = {}
        commit_grid.column['port'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userAttrs'] = {}
        commit_grid.column['username'] = {}
        commit_grid.column['userBaseDN'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userProtoAttr'] = {}
        commit_grid.column['loginUpdateMode'] = {}
        commit_grid.column['userProtoDefault'] = {}
        commit_grid.column['serviceAccountDN'] = {}
        commit_grid.column['userProtoPriority'] = {}
        commit_grid.column['loginAttr'] = {}
        commit_grid.column['applyTagsFunc'] = {}
        commit_grid.column['connectTimeout'] = {}
        commit_grid.column['sysMod'] = {}
        commit_grid.column['readTimeout'] = {}
        commit_grid.column['mod'] = {}

        commit_grid.append({"id": id, 
                            "tls": tls, 
                            "host": host,
                            "port": port,
                            "userAttrs": userAttrs,
                            "userBaseDN": userBaseDN, 
                            "password": password,
                            "userProtoAttr": userProtoAttr,
                            "loginUpdateMode": loginUpdateMode,
                            "userProtoDefault": userProtoDefault, 
                            "serviceAccountDN": serviceAccountDN,
                            "userProtoPriority": userProtoPriority,
                            "loginAttr": loginAttr, 
                            "applyTagsFunc": applyTagsFunc, 
                            "connectTimeout": connectTimeout,
                            "sysMod": sysMod, 
                            "readTimeout": readTimeout,
                            "mod": mod
                            })


        h.call("hostCommit",commit_grid)

def updateLDAPPassword(h,newPass):
        
        result = h.eval("hostSettings(\"ldap\").removeCol(\"is\")").metadata['rec']
        
        id = result['id']
        tls = result['tls'] 
        host = result['host']
        port = result['port']
        userAttrs = result['userAttrs']
        userBaseDN = result['userBaseDN']
        password = newPass
        userProtoAttr = result['userProtoAttr']
        loginUpdateMode = result['loginUpdateMode']
        userProtoDefault = result['userProtoDefault']
        serviceAccountDN = result['serviceAccountDN']
        userProtoPriority = result['userProtoPriority']
        loginAttr = result['loginAttr']
        applyTagsFunc = result['applyTagsFunc']
        connectTimeout = result['connectTimeout']
        sysMod = result['sysMod']
        readTimeout = result['readTimeout']
        mod = result['mod']


        commit_grid = hszinc.Grid()
        commit_grid.column['id'] = {}
        commit_grid.column['tls'] = {}
        commit_grid.column['host'] = {}
        commit_grid.column['port'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userAttrs'] = {}
        commit_grid.column['username'] = {}
        commit_grid.column['userBaseDN'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userProtoAttr'] = {}
        commit_grid.column['loginUpdateMode'] = {}
        commit_grid.column['userProtoDefault'] = {}
        commit_grid.column['serviceAccountDN'] = {}
        commit_grid.column['userProtoPriority'] = {}
        commit_grid.column['loginAttr'] = {}
        commit_grid.column['applyTagsFunc'] = {}
        commit_grid.column['connectTimeout'] = {}
        commit_grid.column['sysMod'] = {}
        commit_grid.column['readTimeout'] = {}
        commit_grid.column['mod'] = {}

        commit_grid.append({"id": id, 
                            "tls": tls, 
                            "host": host,
                            "port": port,
                            "userAttrs": userAttrs,
                            "userBaseDN": userBaseDN, 
                            "password": password,
                            "userProtoAttr": userProtoAttr,
                            "loginUpdateMode": loginUpdateMode,
                            "userProtoDefault": userProtoDefault, 
                            "serviceAccountDN": serviceAccountDN,
                            "userProtoPriority": userProtoPriority,
                            "loginAttr": loginAttr, 
                            "applyTagsFunc": applyTagsFunc, 
                            "connectTimeout": connectTimeout,
                            "sysMod": sysMod, 
                            "readTimeout": readTimeout,
                            "mod": mod
                            })

        h.call("hostCommit",commit_grid)


def updateLDAPProtoPriority(h):
        
        result = h.eval("hostSettings(\"ldap\").removeCol(\"is\")").metadata['rec']
        
        getProtos = h.eval("userProtoReadAll(userProto, { search:\"\" })")
        
        id = result['id']
        tls = result['tls'] 
        host = result['host']
        port = result['port']
        userAttrs = result['userAttrs']
        userBaseDN = result['userBaseDN']
        password = {}
        userProtoAttr = result['userProtoAttr']
        loginUpdateMode = result['loginUpdateMode']
        userProtoDefault = result['userProtoDefault']
        serviceAccountDN = result['serviceAccountDN']

        for proto in getProtos:
            if proto == getProtos[0]:
                userProtoPriority = proto["userProtoName"] 
            else:
                userProtoPriority = userProtoPriority + "," + proto["userProtoName"]  

        loginAttr = result['loginAttr']
        applyTagsFunc = result['applyTagsFunc']
        connectTimeout = result['connectTimeout']
        sysMod = result['sysMod']
        readTimeout = result['readTimeout']
        mod = result['mod']


        commit_grid = hszinc.Grid()
        commit_grid.column['id'] = {}
        commit_grid.column['tls'] = {}
        commit_grid.column['host'] = {}
        commit_grid.column['port'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userAttrs'] = {}
        commit_grid.column['username'] = {}
        commit_grid.column['userBaseDN'] = {}
        commit_grid.column['password'] = {}
        commit_grid.column['userProtoAttr'] = {}
        commit_grid.column['loginUpdateMode'] = {}
        commit_grid.column['userProtoDefault'] = {}
        commit_grid.column['serviceAccountDN'] = {}
        commit_grid.column['userProtoPriority'] = {}
        commit_grid.column['loginAttr'] = {}
        commit_grid.column['applyTagsFunc'] = {}
        commit_grid.column['connectTimeout'] = {}
        commit_grid.column['sysMod'] = {}
        commit_grid.column['readTimeout'] = {}
        commit_grid.column['mod'] = {}

        commit_grid.append({"id": id, 
                            "tls": tls, 
                            "host": host,
                            "port": port,
                            "userAttrs": userAttrs,
                            "userBaseDN": userBaseDN, 
                            "password": password,
                            "userProtoAttr": userProtoAttr,
                            "loginUpdateMode": loginUpdateMode,
                            "userProtoDefault": userProtoDefault, 
                            "serviceAccountDN": serviceAccountDN,
                            "userProtoPriority": userProtoPriority,
                            "loginAttr": loginAttr, 
                            "applyTagsFunc": applyTagsFunc, 
                            "connectTimeout": connectTimeout,
                            "sysMod": sysMod, 
                            "readTimeout": readTimeout,
                            "mod": mod
                            })

        h.call("hostCommit",commit_grid)

def main():
    module = AnsibleModule(
        argument_spec = dict(
           entrocim_hostname = dict(required=True, type='str'),
           entrocim_ldap_host = dict(required=False, type='str'),
           entrocim_ldap_port = dict(required=False, type='str'),
           entrocim_ldap_userAttrs = dict(required=False, type='str'),
           entrocim_ldap_userBaseDN = dict(required=False, type='str'),
           entrocim_ldap_password = dict(required=False, type='str', no_log=True),
           entrocim_ldap_userProtoAttr = dict(required=False, type='str'),
           entrocim_ldap_serviceAccountDN = dict(required=False, type='str'),
           entrocim_ldap_userProtoPriority = dict(required=False, type='str'),
           entrocim_ldap_loginAttr = dict(required=False, type='str'),
           entrocim_ldap_state = dict(default='check',type='str', choices=['add','updatePassword','check','updateProto'])
        ),
        supports_check_mode=True
    )
    h = openHaystackConnection(module.params['entrocim_hostname'],'sys')
    state = module.params["entrocim_ldap_state"]
    if state == "updatePassword":
        updateLDAPPassword(h,module.params['entrocim_ldap_password'])
        result = h.eval("ldapVerifySettings()")[0]['val']
        if "SUCCESS" in result: 
            module.exit_json(changed=False, stdout="Password changed and LDAP connection success")
        else:
            module.fail_json(msg="Password changed and LDAP connection failed")
    elif state == "add":
        addLDAPConfiguration(h,module.params["entrocim_ldap_host"],
                               module.params["entrocim_ldap_port"],
                               module.params["entrocim_ldap_userAttrs"],
                               module.params["entrocim_ldap_userBaseDN"],
                               module.params["entrocim_ldap_password"], 
                               module.params["entrocim_ldap_userProtoAttr"],
                               module.params["entrocim_ldap_serviceAccountDN"],
                               module.params["entrocim_ldap_userProtoPriority"],
                               module.params["entrocim_ldap_loginAttr"]
                            )
        result = h.eval("ldapVerifySettings()")[0]['val']
        if "SUCCESS" in result: 
            module.exit_json(changed=False, stdout="LDAP configuration completed with sucess")
        else:
            module.fail_json(msg="LDAP configuration failed")
    elif state == "updateProto":
        updateLDAPProtoPriority(h)
        result = h.eval("ldapVerifySettings()")[0]['val']
        if "SUCCESS" in result: 
             module.exit_json(changed=False, stdout="Protos applied with success on the LDAP configuration")
        else:
            module.fail_json(msg="Proto configuration failed on the LDAP configuration")
    else:
        result = h.eval("ldapVerifySettings()")[0]['val']
        if "SUCCESS" in result: 
             module.exit_json(changed=False, stdout="LDAP connection is working")
        else:
            module.fail_json(msg="LDAP connection failed")

if __name__ == '__main__':
    main()