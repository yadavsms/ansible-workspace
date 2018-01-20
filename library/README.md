# qemu-img
Image create and convert into different format

# Create a raw disk 
```python
- qemu-img: dest=/var/lib/libvirt/images/test.img disk_type=raw  size=8G state=present force=yes
```
# Create a volume
```python
- qemu_img: name=testing.qcow2 disk_type=volume  size=8G state=present force=yes
```
# Convert image
```python
- qemu-img: src_img=/var/lib/libvirt/images/test5.img dest_img=/var/lib/libvirt/images/test5.qcow2 disk_type=qcow2 state=convert
```

# Delete Raw Disk
```python
- qemu-img: dest=/var/lib/libvirt/images/test4.img  disk_type=raw state=absent
```

# Delete Volume Disk
```python
- qemu-img:  name=test.qcow2  disk_type=volume state=absent
```

# virt-install
Ansible virt-install module with network and bridge(portgroup) support

# Create a new VM with bootstrap from PXE.
``python
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
        portgroup: br0
``
# Create a new VM from an existing Image
``python
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
```
