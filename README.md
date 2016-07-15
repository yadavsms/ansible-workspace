# ansible-workspace
### To install Jenkins:

`CREATE INVENTORY`:

Update the hosts file Under `[jeninks_host]` group.
```
cat inventory/hosts 
[jenkins_host]
jenkins-debian.somesh
jenkins-rhel.somesh
```
And update the IP Address and Credentials in Hosts vars(inventory/host_vars/<host's alias specified in hosts file>)

```
cat inventory/host_vars/jenkins-debian.somesh
ansible_connection: ssh
ansible_ssh_host: 172.16.20.146
ansible_ssh_user: someshy
ansible_ssh_pass: somesh
ansible_sudo_pass: somesh
```
`UPDATE VARS:`

Update the vars in `group_vars/all` file for any version changes.
`Note:` If you are using Debian family OS then only update debian section same is applied with RedHat family OS.
```
cat inventory/group_vars/all 
---
debian:
  java_repo: "ppa:webupd8team/java"
  java_version: java8
  jenkins_apt_key: https://jenkins-ci.org/debian/jenkins-ci.org.key
  jenkins_apt_repo: "deb http://pkg.jenkins-ci.org/debian binary/"
  
redhat:
  jdk_version: jdk-8u91-linux-x64
  jdk_path: /opt/jdk1.8.0_91
  jdk_url: http://download.oracle.com/otn-pub/java/jdk/8u91-b14/jdk-8u91-linux-x64.tar.gz
  jenkins_rpm_repo: http://pkg.jenkins-ci.org/redhat/jenkins.repo
  jenkins_rpm_key: https://jenkins-ci.org/redhat/jenkins-ci.org.key
```

After all the changes, Finally run:

```
cd ansible-workspace
ansible-playbook -i inventory/ playbooks/deploy_jenkins.yml
```
