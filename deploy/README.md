# How to work with the playbooks

## Work with sensitive data

Sensitive content (password, iam, emails e.t.c) should be encrypted by Ansible Vault tool.
Upload vault password from last pass if it exists (or create new) and put it down to a password file (a_password_file)
Launch command to encrypt distinct value:
```sh
ansible-vault encrypt_string --vault-password-file=a_password_file 'password' --name 'name_of_variable'
```

## Launching provisioning roles

```sh
ansible-playbook --vault-password-file=.vault_password --inventory-file=inventory.yml main.yml
```

## Launching cleanup role
```sh
ansible-playbook delete-EC2-testbed.yml -v --extra-vars "delete=true"
```
Set variable to true in order to delete all aws resources (gateway, subnet, route table, vpc) along with ec2 instance

# Resourses Management Rules
## Tags
Each tag is a simple label consisting of a customer-defined key and an optional value
that can make it easier to manage, search for, and filter resources
Required tags:
- **tag:owner** [it_services]
- **tag:stack**
- **tag:name**

#### tag:owner
Describes an owner of the resource. Possible options: it_services.
#### tag:stack
Describes owner of the resource. Possible options: production, build, test.
#### tag:name
| Resource Type  | Example AWS Resource tag:name       | Stack      | Resource  name | Type      | Unique name    |
|----------------|-------------------------------------|------------|----------------|-----------|----------------|
| VPC            | shared.vpc.techops                  | Shared     | -              | vpc       | techops        |
| Gateway        | shared.gw.techops                   | Shared     | -              | gw        | techops        |
| Subnet         | shared.web.public-sn.slack_services | Shared     | web            | public-sn | slack_services |
| Route table    | prod.db.rt.hibob_listener           | Production | db             | rt        | hibob_listener |
| Security group | build.app.sg.jira_proxy             | Build      | app            | sg        | jira_proxy     |
| EC2            | test.app.ec2.slack_bot              | Test       | app            | ec2       | slack_bot      |