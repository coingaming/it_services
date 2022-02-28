terraform {
  required_version = "> 0.13.5"
  backend "s3" {
    bucket = "tfstate-08thbu7uockv8gg"
    key    = "sl-bot-srv-instance"
    region = "eu-central-1"
  }
  required_providers {
    aws = {
      version = "~> 3"
    }
  }
}

provider "aws" {
#  version = "> 3"
  region  = "eu-central-1"
}

data "aws_ami" "ubuntu" {
  most_recent = false

  filter {
    name   = "name"
    values = ["ubuntu-minimal/images/hvm-ssd/ubuntu-impish-21.10-amd64-minimal-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "image-id"
    values = ["ami-022962076e5d742e1"]
  }

  owners = ["099720109477"] # Canonical
}


output "ip" {
  value = aws_eip.sl-bot-srv_eip
}