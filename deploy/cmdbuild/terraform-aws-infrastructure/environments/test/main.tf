# Tags
locals {
  stage_service = "test-iam"
  terraform     = "true"
  env           = "cg-test-iam"
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
  troubleshooter = "176.46.126.158/32,81.20.149.200/32,90.191.33.149/32" #pol-home, CG-office, it-home
}

# Get DB credentials and parse JSON
data "aws_secretsmanager_secret_version" "test_creds" {
  secret_id = "${local.env}-db-admin"
}
locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.test_creds.secret_string
  )
}

# Add SSH keys
resource "aws_key_pair" "test_key" {
  key_name   = "${local.env}-ansible"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC0pUa+Pp6QAuuSjeMluY7yC1YHC7MXFBHY+hpqDwmfj+FrxY8Qg/14BaJ8YRb1njA9LtuQxd1izzKkh2FE9YIkdqy9pbSGEYjKq1FD+u55gLSjLN5x6Cy5lbkPz27C624tbOKod3rqrH/Ow7nXYiDHtu1q++RW+u+ye3SwODCUIjJmsSUZuz4na0b02iviGrzIvnZe9/lbl2bkdiYGXzmiqxjbEaw/amldTi82hRTvjhDu4X108C0xUucxxapf4mONJixBRXLhZQXXyfUPC2UckiKKAagJGaTOeseypKZ86EWexhiR6qmiJjmAX/zWNS2n/D2UujOK5lJ9H1mxmz+DMs1auIuvWzXyDAU2lnZBpgA616Kj016SYeYx3YIelX/CXYIEBHPN6yoiVM769WwCYa5Oie+RGLw5Gfr2T862ldVpY4z65k1viMD6aXFapLg36l/Frz6k8nHLifcZkvCNAcjZSvxMV/CD7kntcW2fYhdNMWZlG212+Jp46ofyihU= ${local.env}-ansible"
}
resource "aws_key_pair" "test_user" {
  key_name   = "${local.env}-user"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDJgAZz5cOL9IeVQ4JG356Rbs5/lio5W1FLd/1xzheA5LSjc/UprqXWh8EwFddYXujNMFSlhLYm2/WZTHAWI2/NP7AKXeKWamEjOvFyNlWUXnCKPWKpmLEWEkKeF6VeIptTU8xt8nlOvaVLMK6iEr9yzRdeFpMfF3qp/s2UP5WXpllgRMIwLBPlzL6mnfUGukH8MJqibCZQ2oaQ8weSXryiRoCdRRnZ5dXo3VYO8dcJEdJqX14/BKvIQ0irR0fM6sQ2lOjoJxpkXtLnhgiBwO/dXhCemQTASHsBG7MxNcv8wgUj6RUUrLK0JeK3tQCVXr1R9tw8TsB1lRZafVhMm+8l ${local.env}-user"
}

# Allocate Elastic IP
resource "aws_eip" "test_eip" {
  vpc      = true
  instance = module.test_ec2.id

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
module "test_vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "cg-infra-security-2"
  cidr = "172.16.2.0/24"

  azs            = ["eu-central-1a", "eu-central-1b"]
  public_subnets = ["172.16.2.0/25", "172.16.2.128/25"]

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
module "test_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 3.0"

  name                    = "${local.env}-app-1"
  key_name                = aws_key_pair.test_user.key_name
  ami                     = data.aws_ami.ubuntu.id
  instance_type           = "t2.medium"
  monitoring              = true
  disable_api_termination = false
  cpu_credits             = "unlimited"

  subnet_id                   = module.test_vpc.public_subnets[0]
  associate_public_ip_address = true

  vpc_security_group_ids = [module.test_security_group.security_group_id]

  root_block_device = [
    {
      volume_type = "gp2"
      volume_size = 8
      enctypted   = true
    },
  ]

  tags        = local.tags
  volume_tags = local.tags
}

# Create Security Group for EC2 instance
module "test_security_group" {
  source = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-app-secgr"
  description = "${local.env}-app-secgr rules"
  vpc_id      = module.test_vpc.vpc_id

  ingress_cidr_blocks = [module.test_vpc.vpc_cidr_block]
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
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      description = "Ingress SSH from specific source"
      cidr_blocks = local.troubleshooter
    },
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Ingress HTTPS from specific source"
      cidr_blocks = local.troubleshooter
    }
  ]

  egress_cidr_blocks = [module.test_vpc.vpc_cidr_block]
  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      description = "Egress All to All"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = local.tags
}

# Create Security Group for DB instance
module "test_security_group_db" {
  source = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-db-secgr"
  description = "${local.env}-db-secgr rules"
  vpc_id      = module.test_vpc.vpc_id

  ingress_cidr_blocks = [module.test_vpc.vpc_cidr_block]
  egress_cidr_blocks  = [module.test_vpc.vpc_cidr_block]

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
module "test_db" {
  source = "terraform-aws-modules/rds/aws"
  version = "~> 3.0"

  identifier = "cg-test-iam-db"

  allocated_storage     = 20
  max_allocated_storage = 21
  storage_type          = "gp2"
  storage_encrypted     = true

  engine               = "postgres"
  engine_version       = "12.7"
  family               = "postgres12"
  major_engine_version = "12"

  instance_class = "db.t2.medium"
  username       = local.db_creds.username
  password       = local.db_creds.password
  port           = "5432"

  subnet_ids = module.test_vpc.public_subnets

  availability_zone = "eu-central-1a"

  backup_retention_period = 7
  backup_window           = "00:05-01:05"

  maintenance_window = "Mon:01:10-Mon:02:10"

  performance_insights_enabled    = true
  monitoring_interval             = 15
  monitoring_role_arn             = "arn:aws:iam::192895540911:role/cg-test-iam-AmazonRDSEnhancedMonitoringRole"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  vpc_security_group_ids = [module.test_security_group_db.security_group_id]

  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = false

  create_db_option_group    = false
  create_db_parameter_group = false

  tags = local.tags
}
