# Tags
locals {
  stage_service = "live-iam"
  terraform     = "true"
  env           = "cg-live-iam"
}

locals {
  tags = {
    Stage-Service = local.stage_service
    Terraform     = local.terraform
  }
}

# Security Group Ingress CIDR blocks
locals {
  mgmt_lnx_ips   = "18.159.97.126/32,35.159.34.2/32" # play-mgmt, live-mgmt
  cloudflare_ips = "173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/12,172.64.0.0/13,131.0.72.0/22"
  troubleshooter = "81.20.149.200/32" #CG-office
}

# Get DB credentials and parse JSON
data "aws_secretsmanager_secret_version" "live_creds" {
  secret_id = "${local.env}-db-admin"
}
locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.live_creds.secret_string
  )
}

# Add SSH key
# Random SSH key used for testing
resource "aws_key_pair" "live_user" {
  key_name   = "${local.env}-user"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCRNIDR2lngvOanxAlrqJVCchBHajYuqvCo3XGf58DNB+bG8SLWJeg//YJYeVfdN9m2iHRmv8/LQxw9ehvt3at2pVntnGyabSfmyOfrmPfxsLCdZl3JmX7wz+fKLwB1N+7jDzY2MFdW7Iqq37hfvWbq5g0zWTQ8+ZqjuCA691izF4F4SJ1PDNJkStqIsOZv3qVN9mg84bOYycxIqh0oTqC9U0HpbOMSMJHPMQ8+wGmAOsnO00axxvoHMrA88CNVBy39qJd3KO/dVkVCQ3RwLo3vuDb3+3uwh2GaWLRMG1NXl8k3Yfv6Zip8DvM1YJpntrtVve55ttyUsSLNmF8hHxut ${local.env}-user"
}

# Allocate Elastic IP
resource "aws_eip" "live_eip" {
  vpc      = true
  instance = module.live_ec2.id

  tags = merge(
    local.tags,
    {
      Name = "${local.env}-app-1-eip"
    },
  )
}

# Find AMI ID for the instance
# In case of new instance installation or complete re-deployment updare filter:
# 1) "name" with "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" value
# 2) "image-id" with most recent image ID
data "aws_ami" "ubuntu" {
  most_recent = false

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "image-id"
    values = ["ami-07d1bb89ff2dd50fe"]
  }

  owners = ["099720109477"] # Canonical
}

# Create VPC
module "live_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "cg-infra-security-1"
  cidr = "172.16.1.0/24"

  azs            = ["eu-central-1a", "eu-central-1b"]
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

# Create EC2 instance
module "live_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 3.0"

  name                    = "${local.env}-app-1"
  key_name                = aws_key_pair.live_user.key_name
  ami                     = data.aws_ami.ubuntu.id
  instance_type           = "t2.large"
  monitoring              = true
  disable_api_termination = true
  cpu_credits             = "unlimited"

  subnet_id                   = module.live_vpc.public_subnets[0]
  associate_public_ip_address = true


  vpc_security_group_ids = [module.live_security_group.security_group_id]

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
module "live_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-app-secgr"
  description = "${local.env}-app-secgr rules"
  vpc_id      = module.live_vpc.vpc_id

  ingress_cidr_blocks = [module.live_vpc.vpc_cidr_block]
  ingress_with_cidr_blocks = [
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "Ingress SSH from all mgmt-lnx"
      cidr_blocks = local.mgmt_lnx_ips
    },
    {
      from_port   = 8080
      to_port     = 8080
      protocol    = "tcp"
      description = "Ingress HTTP Alternative from all mgmt-lnx"
      cidr_blocks = local.mgmt_lnx_ips
    },
    {
      from_port   = 80
      to_port     = 80
      protocol    = "tcp"
      description = "Ingress HTTP from all mgmt-lnx"
      cidr_blocks = local.mgmt_lnx_ips
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Ingress HTTPS from all mgmt-lnx"
      cidr_blocks = local.mgmt_lnx_ips
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Ingress HTTPS from Cloudflare"
      cidr_blocks = local.cloudflare_ips
    }
  ]

  egress_cidr_blocks = [module.live_vpc.vpc_cidr_block]
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
module "live_security_group_db" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-db-secgr"
  description = "${local.env}-db-secgr rules"
  vpc_id      = module.live_vpc.vpc_id

  ingress_cidr_blocks = [module.live_vpc.vpc_cidr_block]
  egress_cidr_blocks  = [module.live_vpc.vpc_cidr_block]

  ingress_rules = ["postgresql-tcp"]
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "Ingress PostgreSQL from all mgmt-lnx"
      cidr_blocks = local.mgmt_lnx_ips
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
module "live_db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 2.0"

  identifier = "cg-live-iam-db"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true

  engine               = "postgres"
  engine_version       = "12.7"
  family               = "postgres12"
  major_engine_version = "12"

  instance_class = "db.m5.large"
  username       = local.db_creds.username
  password       = local.db_creds.password
  port           = "5432"

  subnet_ids = module.live_vpc.public_subnets

  availability_zone = "eu-central-1a"

  backup_retention_period = 31
  backup_window           = "00:05-01:05"

  maintenance_window = "Mon:01:10-Mon:02:10"

  performance_insights_enabled    = true
  monitoring_interval             = 15
  monitoring_role_arn             = "arn:aws:iam::192895540911:role/cg-live-iam-AmazonRDSEnhancedMonitoringRole"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  vpc_security_group_ids = [module.live_security_group_db.security_group_id]

  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = true

  create_db_option_group    = false
  create_db_parameter_group = false

  tags = local.tags
}