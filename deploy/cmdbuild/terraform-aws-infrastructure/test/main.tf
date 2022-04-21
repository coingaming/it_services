locals {
  stage_service = "cmdbuild-srv_test"
  terraform     = "true"
  env           = "yolo-cmdbuild-srv_test"
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
  secret_id = "test-cmdbuild-ready2use-postgresql"
}

locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.cmdbuild_creds.secret_string
  )
}

resource "aws_key_pair" "cmdbuild-test_srv_user" {
  key_name   = "ec2_keypair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC2lPhGI/etrPGqx/1ewboeNiKFmFFlVlOddp4kYx5cwZajQztLNgMal8xlIVgw2nSxCqCzj0YPkLJ95W9CBA0TM5PFvAUPFE1tSd37Ofs3nX/WKsTXQ8JbjmjCE0IUoj5Zfc2eDS39q6HVGZGZPrODkhDEzfsDbQHoU5zGoVX7aPzmND+J2Deln+PXaLVsjochyPxCHDkMF6in/2aApm5Hdpt76b/5iK+Gg2k77MKRvxma/beBHRYeZBGeedXqVj6Xo6CESSEMcwWpb5Tz3zewiIfVPV5JRsk4aoWw9AsAmvGpmoYeIAYWJ8jXyQA2HtAn8WCFEw7uWeWev3Q5/u51UGrt8HQmYPYn6Hft2spa0/SWDmjiGykBi1vYEYf0Liijg1+oX0uzYRwNHUiAdopzlwfhh2GJh39TMCOxMMY26R0nhIZMw7ZeK7trVhOrKFWCtWz0+32yMeErxn1H31hVmwDMcStFi5ySM4E7A7dUjqlYZNvyVEjd6qhVwy7zMi0= vladislav@vladislav-ThinkPad-P15v-Gen-2i"
}

resource "aws_eip" "cmdbuild-test_srv_eip" {
  vpc      = true
  instance = module.cmdbuild-test_srv_ec2.id[0]

  tags = merge(
    local.tags,
    {
      Name = "${local.env}-app-1-eip"
    },
  )
}

module "cmdbuild-test_srv_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "cmdbuild-infra-security-2"
  cidr = "172.16.2.0/24"

  azs            = ["eu-west-1a", "eu-west-1b"]
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

module "cmdbuild-test_srv_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  name                        = "${local.env}-app-1"
  instance_count              = "1"
  key_name                    = aws_key_pair.cmdbuild-test_srv_user.key_name
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.medium"
  monitoring                  = true
  disable_api_termination     = false
  subnet_id                   = module.cmdbuild-test_srv_vpc.public_subnets[0]
  associate_public_ip_address = true
  vpc_security_group_ids = [module.cmdbuild-app-test_srv_security_group.this_security_group_id]

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
module "cmdbuild-app-test_srv_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "cmdbuild-app-srv-secgr"
  description = "cmdbuild-app-srv-secgr rules"
  vpc_id      = module.cmdbuild-test_srv_vpc.vpc_id

  ingress_cidr_blocks = [module.cmdbuild-test_srv_vpc.vpc_cidr_block]
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

  egress_cidr_blocks = [module.cmdbuild-test_srv_vpc.vpc_cidr_block]
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
module "cmdbuild-db-test_srv_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4.0"

  name        = "${local.env}-db-secgr"
  description = "${local.env}-db-secgr rules"
  vpc_id      = module.cmdbuild-test_srv_vpc.vpc_id

  ingress_cidr_blocks = [module.cmdbuild-test_srv_vpc.vpc_cidr_block]
  egress_cidr_blocks = [module.cmdbuild-test_srv_vpc.vpc_cidr_block]

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
module "cmdbuild-test_srv_db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 2.0"

  identifier = "cmdbuild-test-db-1"

  allocated_storage     = 20
  max_allocated_storage = 30
  storage_type          = "gp2"
  storage_encrypted     = true

  engine               = "postgres"
  engine_version       = "13.4"
  family               = "postgres13"
  major_engine_version = "13"

  instance_class = "db.t4g.medium"
  username       = local.db_creds.username
  password       = local.db_creds.password
  port           = "5432"

  subnet_ids = module.cmdbuild-test_srv_vpc.public_subnets

  availability_zone = "eu-west-1a"

  backup_retention_period = 31
  backup_window           = "00:05-01:05"

  maintenance_window = "Mon:01:10-Mon:02:10"

  performance_insights_enabled    = true
  monitoring_interval             = 15
  monitoring_role_arn             = "arn:aws:iam::192895540911:role/test-cmdbuild-AmazonRDSEnhancedMonitoringRole"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  vpc_security_group_ids = [module.cmdbuild-db-test_srv_security_group.security_group_id]

  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = false

  create_db_option_group    = false
  create_db_parameter_group = false

  tags = local.tags
}

data "aws_db_snapshot" "latest_prod_snapshot" {
  db_instance_identifier = module.cmdbuild-test_srv_db.this_db_instance_id
  most_recent            = true
}

# Create DB restored from the latest snapshot
resource "aws_db_instance" "cmdbuild-restored_test_srv_db" {

  identifier = "cmdbuild-test-db-2"

  snapshot_identifier = data.aws_db_snapshot.latest_prod_snapshot.id
  lifecycle {
    ignore_changes = [
      snapshot_identifier,
    ]
  }

  allocated_storage     = 20
  max_allocated_storage = 30
  storage_type          = "gp2"
  storage_encrypted     = true

  engine               = "postgres"
  engine_version       = "13.4"

  instance_class = "db.t4g.medium"
  username       = local.db_creds.username
  password       = local.db_creds.password
  port           = "5432"

  db_subnet_group_name = module.cmdbuild-test_srv_db.this_db_subnet_group_id #"cmdbuild-test-db-1-20220411122353548800000003"

  availability_zone = "eu-west-1a"

  backup_retention_period = 31
  backup_window           = "00:05-01:05"

  maintenance_window = "Mon:01:10-Mon:02:10"

  performance_insights_enabled    = true
  monitoring_interval             = 15
  monitoring_role_arn             = "arn:aws:iam::192895540911:role/test-cmdbuild-AmazonRDSEnhancedMonitoringRole"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  vpc_security_group_ids = [module.cmdbuild-db-test_srv_security_group.security_group_id]

  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = false

  tags = local.tags
}