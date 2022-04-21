locals {
  stage_service = "cmdbuild-srv_prod"
  terraform     = "true"
  env           = "yolo-cmdbuild-srv_prod"
}

locals {
  tags = {
    Stage-Service = local.stage_service
    Terraform     = local.terraform
  }
}

locals {
  offices_ips = "81.20.149.200/32,35.158.4.35/32"
}

# Get DB credentials and parse JSON
data "aws_secretsmanager_secret_version" "cmdbuild_creds" {
  secret_id = "prod-cmdbuild-ready2use-postgresql"
}

locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.cmdbuild_creds.secret_string
  )
}

resource "aws_key_pair" "cmdbuild-srv_user" {
  key_name   = "prod-cmdbuild-user"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCwjnjz44ovMslgrvtRKGVucdtwxwW3oPhCDAWCpNXSoWziU+smxszz/jq7s8V94OnT9qHyQfuzzpsGiHV3yN72LzfgsCwaOtpvSH3CZtYrfdn0dDBp2gqMxk0zT2vTdY/q5qJk9T3HO308gSf3RreIHA1DpIVPAg6dcpeAzX0oTAheQi7XAGG2wYBrQYqeRTRZYtu0vlBncdNsRWJeaBfH/6cKxyEG6TqymYNjQnZDQtZnSL/AihRgmLmba4UpHvxYSztOmHMMvJ7I6EKsXa+g7gofZm0PVYgLvufNbbQ6iLbpfv4sk3Am8KwwLZY07Pn7gvrP63i2bk03MKQC7AAP vladislav@vladislav-ThinkPad-P15v-Gen-2i"
}

resource "aws_eip" "cmdbuild-srv_eip" {
  vpc      = true
  instance = module.cmdbuild-prod_srv_ec2.id[0]

  tags = merge(
    local.tags,
    {
      Name = "${local.env}-app-1-eip"
    },
  )

}

module "cmdbuild-prod_srv_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "cmdbuild-infra-security-1"
  cidr = "172.16.1.0/24"

  azs            = ["eu-west-1a", "eu-west-1b"]
  public_subnets = ["172.16.1.0/25", "172.16.1.128/25"]

  create_database_subnet_group           = true
  create_database_subnet_route_table     = true
  create_database_internet_gateway_route = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags               = local.tags
  public_subnet_tags = local.tags
  vpc_tags           = local.tags
}

module "cmdbuild-prod_srv_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  name                        = "${local.env}-app-1"
  instance_count              = "1"
  key_name                    = aws_key_pair.cmdbuild-srv_user.key_name
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.xlarge"
  monitoring                  = true
  disable_api_termination     = false
  subnet_id                   = module.cmdbuild-prod_srv_vpc.public_subnets[0]
  associate_public_ip_address = true
  vpc_security_group_ids = [module.cmdbuild-app-prod_srv_security_group.this_security_group_id]

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 10
      enctypted   = true
    },
  ]

  tags        = local.tags
  volume_tags = local.tags
}

# Create Security Group for EC2 instance
module "cmdbuild-app-prod_srv_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "cmdbuild-app-srv-secgr"
  description = "cmdbuild-app-srv-secgr rules"
  vpc_id      = module.cmdbuild-prod_srv_vpc.vpc_id

  ingress_cidr_blocks = [module.cmdbuild-prod_srv_vpc.vpc_cidr_block]
  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "From Office SSH"
      cidr_blocks = local.offices_ips
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Infress HTTPS from All"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      description = "Infress HTTPS from All"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  egress_cidr_blocks = [module.cmdbuild-prod_srv_vpc.vpc_cidr_block]
  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "Egress All"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = local.tags
}

# Create Security Group for DB instance
module "cmdbuild-db-prod_srv_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-db-secgr"
  description = "${local.env}-db-secgr rules"
  vpc_id      = module.cmdbuild-prod_srv_vpc.vpc_id

  ingress_cidr_blocks = [module.cmdbuild-prod_srv_vpc.vpc_cidr_block]
  egress_cidr_blocks = [module.cmdbuild-prod_srv_vpc.vpc_cidr_block]

  ingress_rules = ["postgresql-tcp"]
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "Ingress PostgreSQL from all mgmt-lnx"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "tcp"
      description = "Allow PostgreSQL egress"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = local.tags
}

# Create DB
module "cmdbuild-prod_srv_db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 2.0"

  identifier = "cmdbuild-production-db-1"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  engine               = "postgres"
  engine_version       = "13.4"
  family               = "postgres13"
  major_engine_version = "13"

  instance_class = "db.m5.large"
  username       = local.db_creds.username
  password       = local.db_creds.password
  port           = "5432"

  subnet_ids = module.cmdbuild-prod_srv_vpc.public_subnets

  availability_zone = "eu-west-1a"

  backup_retention_period = 31
  backup_window           = "00:05-01:05"

  maintenance_window = "Mon:01:10-Mon:02:10"

  performance_insights_enabled    = true
  monitoring_interval             = 15
  monitoring_role_arn             = "arn:aws:iam::192895540911:role/prod-cmdbuild-AmazonRDSEnhancedMonitoringRole"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  vpc_security_group_ids = [module.cmdbuild-db-prod_srv_security_group.security_group_id]

  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = true

  create_db_option_group    = false
  create_db_parameter_group = false

  tags = local.tags
}