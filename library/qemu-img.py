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
module: qemu-img
short_description: Makes raw and volume storage disk
description:
  - This module creates raw and volume storage disk
version_added: "1.1"
options:
  name:
    description:
    - Name of volume(Required when disk_type is volume)
  dest:
    description:
    - path of raw disk( Required when disk_type is raw).
  format:
    description:
    - format of image(img/qcow2)
  disk_type:
    description:
    - type of disk(raw or volume)
  pool:
    description:
    - pool name(required if disk_type is volume)
  src_img:
    description:
    - path of the source image( Required when state=convert)
  dest_img:
    description:
    - path of the destination image( Required when state=convert)
  size:
    description:
    - size of the disk and volume
  state:
    choices=['present','convert', 'absent']
    description:
    - choose one of the choice
    required= True
  force:
    choices: [ "yes", "no" ]
    default: "no"
    description:
    - If yes, allows to create new disk and volume to override already exists.
    required: false
'''

EXAMPLES = '''
# Create a raw disk 
- qemu-img: dest=/var/lib/libvirt/images/test.img disk_type=raw  size=8G state=present force=yes

# Create a volume 
- qemu_img: name=testing.qcow2 disk_type=volume  size=8G state=present force=yes

# Convert image
- qemu-img: src_img=/var/lib/libvirt/images/test5.img dest_img=/var/lib/libvirt/images/test5.qcow2 disk_type=qcow2 state=convert

# Delete Raw Disk
- qemu-img: dest=/var/lib/libvirt/images/test4.img  disk_type=raw state=absent

# Delete Volume Disk
- qemu-img:  name=test.qcow2  disk_type=volume state=absent
'''


import os

def main():
    module = AnsibleModule(
        argument_spec = dict(
            name=dict(type='str'),
            dest=dict(type='str'),
            format=dict(type='str', default='qcow2'),
            disk_type=dict(type='str', required=True),
            pool=dict(type='str', default='default'),
            src_img=dict(type='str'),
            dest_img=dict(type='str'),
            force=dict(type='bool', default='no'),
            size=dict(type='str'),
            state=dict(type='str', choices=['present','convert', 'absent'], required=True)
        ),
    supports_check_mode=True,
    )
    changed = False
    qemu_img = module.get_bin_path('qemu-img', required=True)
    virsh=module.get_bin_path('virsh', required=True)

    name=module.params['name']
    dest=module.params['dest']
    img_format=module.params['format']
    disk_type=module.params['disk_type']
    pool=module.params['pool']
    src_img=module.params['src_img']
    dest_img=module.params['dest_img']
    size=module.params['size']
    state=module.params['state']
    force=module.boolean(module.params['force'])

    check_vol="%s vol-info %s --pool %s " %(virsh, name, pool)
  
    if state == 'present':
        if disk_type == 'raw':
            if not os.path.exists(dest):
                module.run_command('%s create -f %s "%s" %s' %(qemu_img, img_format, dest, size), check_rc=True)
            elif not force:
                module.fail_json(msg="disk %s is already exists use force=yes to override" % dest)
            elif force:
                os.remove(dest)
                module.run_command('%s create -f %s  "%s" %s' %(qemu_img, img_format, dest, size), check_rc=True)
        elif disk_type == 'volume':
            rc,out,err = module.run_command(check_vol)
            if not rc and not force:
                module.fail_json(msg="Volume %s is already exists use force=yes to override" % name)
            elif rc and force:
                module.run_command('%s vol-delete --pool %s %s' %(virsh, pool, name))
                module.run_command('%s vol-create-as %s %s %s' %(virsh, pool, name, size), check_rc=True )
        changed = True


    if state =='convert':
        module.run_command("%s convert -O %s %s %s" %(qemu_img, format, src_img, dest_img ))
        module.run_command(cmd)
    if state == 'absent':
        if disk_type == 'raw':
            if os.path.exists(dest):
                os.remove(dest)
        elif disk_type == 'volume':
            module.run_command('%s vol-delete --pool %s %s' %(virsh, pool, name))
    changed=True
    module.exit_json(changed=changed)

# import module snippets
from ansible.module_utils.basic import *
main()
