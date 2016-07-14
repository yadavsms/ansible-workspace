# ansible-workspace
### To install Jenkins:

Please Update the inventory `hosts` and `host_vars(inventory/host_vars/<host's alias specified in hosts file>)` with IpAddress and login credentials and `group_vars/all` file for any version changes
After all the changes, run:

```
cd ansible-workspace
ansible-playbook -i inventory/ playbooks/deploy_jenkins.yml
```
