##
# MyVault API - Ansible module
#!/usr/bin/python3
##

from ansible.module_utils.basic import *
import ansible.module_utils.cyberarkDell as cyberarkDell

def main():
    module = AnsibleModule(
        argument_spec = dict(
           vault_hid = dict(required=True, type='str'),
           vault_authn = dict(required=True, type='str'),
           vault_secret = dict(required=True, type='str')
        ),
        supports_check_mode=True
    )
    m = cyberarkDell.myvault(module.params['vault_hid'],module.params['vault_authn'],module.params['vault_secret'])
    password = m.getPassword() 
    if password == False:
        module.fail_json(msg="Couldn't establish connection with API, please check parameters")
    else:
        module.exit_json(changed=False, stdout=password)

if __name__ == '__main__':
    main()