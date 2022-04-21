terraform {
  required_version = "> 0.13.5"
  backend "s3" {
    bucket = "tfstate-prod-cmdbuild"
    key    = "prod-cmdbuild-s3-instance"
    region = "eu-west-1"
  }
  required_providers {
    aws = {
      version = "~> 3"
    }
  }
}

provider "aws" {
#  version = "> 3"
  region  = "eu-west-1"
}

data "aws_ami" "ubuntu" {
  most_recent = false

  #filter {
  #  name   = "name"
  #  values = ["ubuntu-minimal/images/hvm-ssd/ubuntu-impish-21.10-amd64-minimal-*"]
  #}
#
  #filter {
  #  name   = "virtualization-type"
  #  values = ["hvm"]
  #}

  filter {
    name   = "image-id"
    values = ["ami-05f9f61e6c95c7d1f"]
  }

  owners = ["099720109477"] # Canonical
}


output "ip" {
  value = aws_eip.cmdbuild-srv_eip
}