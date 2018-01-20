#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Somesh Yadav <yadavsms@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
author: "Somesh Yadav (@yadavsms)"
module: virtinstall
short_description: Launch the VMs on OVS switch with portgroup
description:
  - This module creates Virtual Machines
version_added: "1.1"
options:
  name:
    description:
    - Name of the Virtual Machine
    required: true
  ram:
    description:
    - Physical memory
    required: true
  vcpus:
    description:
    - Number of Virtual CPUs
    required: true
  virt_type: 
    description:                                                                                                                                            
    - Virtualization type                                                                                                                                
    default: "kvm"
  os_type: 
    description:                                                                                                                                            
    - Operating System type                                                                                                                                
    default: "linux" 
  disk: 
    description:                                                                                                                                            
    - Required disks (input as list)
    required: true
  network: 
    description:                                                                                                                                            
    - Required networks (input as dict with portgroup)
    required: true 
  pxe:
    choices: [ "True", "False" ]
    description:
    - Bootstrap with pxe server
    default: "False"
  import_image:
    choices: [ "yes", "no" ]
    description:
    - launch vm from image
    default: "no"
  force:
    choices: [ "yes", "no" ]
    default: "no"
    description:
    - If yes, allows to create new VM and override the old VM. 
    required: false
'''

EXAMPLES = '''
# Create a new VM with bootstrap from PXE.
- virtinstall:
    name: test1
    ram: 1024
    vcpus: 2
    virt_type: kvm
    pxe: True
    disk: ['/var/lib/libvirt/images/osdisk.img','/var/lib/libvirt/images/appdisk.img']
    network:
      pxe_interface:
        virt_network: bond0 
        portgroup: pg198
      public_interface:
        virt_network: bond1 
        portgroup: pg2001

- virtinstall:
    name: test1
    ram: 1024
    vcpus: 2
    virt_type: kvm
    pxe: True
    disk: ['/var/lib/libvirt/images/osdisk.img','/var/lib/libvirt/images/appdisk.img']
    network:
      pxe_interface:
        bridge: virbr0
      public_interface:
        bridge: br0
     

# Create a new VM from an existing Image
- virtinstall:
    name: test1
    ram: 1024
    vcpus: 2
    virt_type: kvm
    disk: ['/var/lib/libvirt/images/osdisk.img','/var/lib/libvirt/images/appdisk.img']
    network:
      pxe_interface:
        bridge: virbr0
        portgroup: br0
    image_import: True
'''

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name=dict(type='str', required=True),
            ram=dict(type='str', default=1024),
            vcpus=dict(type='str', default=1),
            os_type=dict(type='str', default='linux'),
            virt_type=dict(type='str', default='kvm'),
            disk=dict(type='list', required=True),
            network=dict(type='dict', required=True),
            pxe=dict(type='bool', default='no'),
            image_import=dict(type='bool', default='no'),
            opts=dict(),
            force=dict(type='bool', default='no')
        ),
        supports_check_mode=True,
    )

    name = module.params['name']
    ram = module.params['ram']
    vcpus = module.params['vcpus']
    os_type = module.params['os_type']
    virt_type = module.params['virt_type']
    disk = module.params.get('disk')
    network = module.params.get('network')
    pxe = module.boolean(module.params['pxe'])
    image_import = module.boolean(module.params['image_import'])
    force = module.boolean(module.params['force'])


    DESTROY = "virsh destroy %s" %name
    UNDEFINE = "virsh undefine %s" %name

    changed = False

    if not os.path.exists('/usr/bin/virt-install'):
        module.fail_json(msg="virtinst package is not installed.")
    def dict_to_param(param_dict):
	string = ""
	for key, value in param_dict.items():
            if "portgroup" in value:
                string += "--network " + "network=" + value['virt_network'].strip() + ",portgroup=" + value['portgroup'].strip() + ",model=virtio "
            else:
                string += "--network " + "bridge=" + value['bridge'].strip() + ",model=virtio"
	return string

    def list_to_param(param_list):
        disk_str=""
        for param in param_list:
            disk_str += "--disk" + " path=" + param + ",cache=none,device=disk,bus=virtio"
        return disk_str

    import libvirt
    try:
        conn = libvirt.openReadOnly('qemu:///system')
        raw_vm = conn.lookupByName(name)
        if raw_vm:
            raw_vm_name = raw_vm.name()
    except libvirt.libvirtError:
        raw_vm_name = ""
    
    if raw_vm_name == name and not force:
        if raw_vm.isActive():
            module.exit_json(changed=changed)
        else:
            module.fail_json(msg="%s already exists use force=yes to override" %name)

    if module.check_mode:
        changed = True
    else:
        virt_install = module.get_bin_path('virt-install', required=True)
        pxe_cmd = "%s --name=%s --ram=%s --vcpus=%s,cores=%s  --virt-type=%s --os-type=%s --pxe %s --noautoconsole %s" %(virt_install, name, ram, vcpus, vcpus, virt_type, os_type, list_to_param(disk), dict_to_param(network))
        import_cmd = "%s --name=%s --ram=%s --vcpus=%s,cores=%s --virt-type=%s --os-type=%s %s --noautoconsole %s --import" %(virt_install, name, ram, vcpus, vcpus, virt_type, os_type, list_to_param(disk), dict_to_param(network))
        if pxe and force:
            # first destroy the vm
            module.run_command(DESTROY)
            # Undefine the vm
            module.run_command(UNDEFINE)
            cmd = pxe_cmd
        elif pxe:
            cmd = pxe_cmd
        elif image_import and force:
            # first destroy the vm                                                                                                                         
            module.run_command(DESTROY)
            # Undefine the vm                                                                                                                              
            module.run_command(UNDEFINE)
            cmd = import_cmd
        elif image_import:
            cmd = import_cmd
        rc,_,err = module.run_command(cmd)
        if rc == 0:
            changed = True
        else:
            module.fail_json(msg="failed to launch the vm ", rc=rc, err=err)
    module.exit_json(changed=changed)
        
# import module snippets
from ansible.module_utils.basic import *
main()
