#!/usr/bin/python3
from __future__ import (absolute_import, division, print_function)
import sys
__metaclass__ = type

DOCUMENTATION = r'''
    name: hosts
    plugin_type: inventory
    short_description: Returns Ansible inventory from INI file
    description: Returns Ansible inventory from INI file
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ['hosts']
      ini_file:
        description: File of the INI inventory file
        required: true
      vault_svc_npdevheptapcf:
        description: Information about vault account svc_npdevheptapcf to get password from myvault
        required: true
      vault_svc_prdprdpheptapcf:
        description: Information about vault account svc_prdprdpheptapcf to get password from myvault
        required: true 
'''

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleParserError                      
import configparser

sys.path.insert(0, 'playbook/module_utils') #workaround to get module_utils
import cyberarkDell as cyberarkDell

class InventoryModule(BaseInventoryPlugin):
    NAME = 'hosts'

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('hosts.yaml',
                              'hosts.yml')):
                valid = True
        return valid

    def _populate(self):
        '''Return the hosts and groups'''
        self.inventory_file = self.inv_file
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.inv_file)
        for section in config.sections():
            if not "vars" in section: 
                self.inventory.add_group(section)
                for option in config.options(section):
                    self.inventory.add_host(option, group=section)
            else:
                group = section.replace(':vars','')
                self.inventory.add_group(group)
                for option in config.options(section):
                    self.inventory.set_variable(group,option,config.get(section, option))
                    if "svc_npdevheptapcf" in config.get(section, option):
                        m = cyberarkDell.myvault(self.vault_svc_npdevheptapcf['hid'],
                                                 self.vault_svc_npdevheptapcf['authn'].data,
                                                 self.vault_svc_npdevheptapcf['secret'])
                        self.inventory.set_variable(group,"ansible_password",m.getPassword())
                    elif "svc_prdprdpheptapcf" in config.get(section, option):
                         m = cyberarkDell.myvault(self.vault_svc_prdprdpheptapcf['hid'],
                                                  self.vault_svc_prdprdpheptapcf['authn'].data,
                                                  self.vault_svc_prdprdpheptapcf['secret'])
                         self.inventory.set_variable(group,"ansible_password",m.getPassword())

    def parse(self, inventory, loader, path, cache):
        '''Return dynamic inventory from source '''
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        # Read the inventory YAML file
        self._read_config_data(path)
        try:
            # Store the options from the YAML file
            self.plugin = self.get_option('plugin')
            self.inv_file = self.get_option('ini_file')

            #getting dictionary information about vault for the service account
            self.vault_svc_npdevheptapcf = {}
            self.vault_svc_npdevheptapcf = self.get_option('vault_svc_npdevheptapcf')

            self.vault_svc_prdprdpheptapcf = {}
            self.vault_svc_prdprdpheptapcf = self.get_option('vault_svc_prdprdpheptapcf')
        except Exception as e:
            raise AnsibleParserError(
                'All correct options required: {}'.format(e))
        # Call our internal helper to populate the dynamic inventory
        self._populate()