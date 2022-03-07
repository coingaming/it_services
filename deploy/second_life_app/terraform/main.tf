locals {
  stage_service = "sl-bot-srv_prod"
  terraform     = "true"
  env           = "yolo-sl-bot-srv_prod"
}

locals {
  tags = {
    Stage-Service = local.stage_service
    Terraform     = local.terraform
  }
}

locals {
  cloudflare_ips = "173.245.48.0/20,103.21.244.0/22,103.22.200.0/22,103.31.4.0/22,141.101.64.0/18,108.162.192.0/18,190.93.240.0/20,188.114.96.0/20,197.234.240.0/22,198.41.128.0/17,162.158.0.0/15,104.16.0.0/12,172.64.0.0/13,131.0.72.0/22"
  offices_ips = "81.20.149.200/32,35.158.4.35/32"
}

#resource "aws_key_pair" "sl-bot-srv_user" {
#  key_name   = "${local.env}-itruu"
#  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCRNIDR2lngvOanxAlrqJVCchBHajYuqvCo3XGf58DNB+bG8SLWJeg//YJYeVfdN9m2iHRmv8/LQxw9ehvt3at2pVntnGyabSfmyOfrmPfxsLCdZl3JmX7wz+fKLwB1N+7jDzY2MFdW7Iqq37hfvWbq5g0zWTQ8+ZqjuCA691izF4F4SJ1PDNJkStqIsOZv3qVN9mg84bOYycxIqh0oTqC9U0HpbOMSMJHPMQ8+wGmAOsnO00axxvoHMrA88CNVBy39qJd3KO/dVkVCQ3RwLo3vuDb3+3uwh2GaWLRMG1NXl8k3Yfv6Zip8DvM1YJpntrtVve55ttyUsSLNmF8hHxut ${local.env}-itruu"
#}

resource "aws_key_pair" "sl-bot-srv_user" {
  key_name   = "ec2_keypair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC2lPhGI/etrPGqx/1ewboeNiKFmFFlVlOddp4kYx5cwZajQztLNgMal8xlIVgw2nSxCqCzj0YPkLJ95W9CBA0TM5PFvAUPFE1tSd37Ofs3nX/WKsTXQ8JbjmjCE0IUoj5Zfc2eDS39q6HVGZGZPrODkhDEzfsDbQHoU5zGoVX7aPzmND+J2Deln+PXaLVsjochyPxCHDkMF6in/2aApm5Hdpt76b/5iK+Gg2k77MKRvxma/beBHRYeZBGeedXqVj6Xo6CESSEMcwWpb5Tz3zewiIfVPV5JRsk4aoWw9AsAmvGpmoYeIAYWJ8jXyQA2HtAn8WCFEw7uWeWev3Q5/u51UGrt8HQmYPYn6Hft2spa0/SWDmjiGykBi1vYEYf0Liijg1+oX0uzYRwNHUiAdopzlwfhh2GJh39TMCOxMMY26R0nhIZMw7ZeK7trVhOrKFWCtWz0+32yMeErxn1H31hVmwDMcStFi5ySM4E7A7dUjqlYZNvyVEjd6qhVwy7zMi0= vladislav@vladislav-ThinkPad-P15v-Gen-2i"
}


resource "aws_eip" "sl-bot-srv_eip" {
  vpc      = true
  instance = module.sl-bot-srv_ec2.id[0]

  tags = merge(
    local.tags,
    {
      Name = "${local.env}-app-1-eip"
    },
  )

}


module "sl-bot-srv_vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> v2.0"

  name = "sl-bot-srv-1"
  cidr = "172.21.0.0/25"

  azs            = ["eu-central-1a"]
  public_subnets = ["172.21.0.0/26"]

  tags               = local.tags
  public_subnet_tags = local.tags
  vpc_tags           = local.tags
}

module "sl-bot-srv_ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 2.0"

  name                        = "${local.env}-lnx-1"
  instance_count              = "1"
  key_name                    = aws_key_pair.sl-bot-srv_user.key_name
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t2.micro"
  monitoring                  = true
  disable_api_termination     = false
  subnet_id                   = module.sl-bot-srv_vpc.public_subnets[0]
  private_ips                 = ["172.21.0.15"]
  associate_public_ip_address = true
  vpc_security_group_ids = [module.sl-bot-srv_security_group.this_security_group_id]

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
module "sl-bot-srv_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3.0"

  name        = "sl-bot-srv-lnx-secgr"
  description = "sl-bot-srv-lnx-secgr rules"
  vpc_id      = module.sl-bot-srv_vpc.vpc_id

  ingress_cidr_blocks = [module.sl-bot-srv_vpc.vpc_cidr_block]
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
  ]

  egress_cidr_blocks = [module.sl-bot-srv_vpc.vpc_cidr_block]
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