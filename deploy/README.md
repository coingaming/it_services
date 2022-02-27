# How to work with the playbooks
# Resourses Management Rules
## Tags
Each tag is a simple label consisting of a customer-defined key and an optional value
that can make it easier to manage, search for, and filter resources
Required tags:
- **tag:owner** [it_services]
- **tag:stack** [production, build, test, shared]
- **tag:name**

#### tag:owner
Describes an owner of the resource. Possible options: it_services.
#### tag:stack
Describes owner of the resource. Possible options: production, build, test.
#### tag:name
| Resource Type  | Example AWS Resource tag:name       | Stack      | Resource  name | Type      | Unique name    |
|----------------|-------------------------------------|------------|----------------|-----------|----------------|
| VPC            | shared.vpc.techops                  | Shared     | -              | vpc       | techops        |
| Subnet         | shared.web.public-sn.slack_services | Shared     | web            | public-sn | slack_services |
| Route table    | prod.db.rt.hibob_listener           | Production | db             | rt        | hibob_listener |
| Security group | build.app.sg.jira_proxy             | Build      | app            | sg        | jira_proxy     |
| EC2            | test.app.ec2.slack_bot              | Test       | app            | ec2       | slack_bot      |