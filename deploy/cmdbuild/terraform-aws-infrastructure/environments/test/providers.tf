terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
  backend "s3" {
    bucket = "tfstate-41c0wnz5vk5e"
    key    = "cg-test-iam"
    region = "eu-central-1"
  }

  required_version = "~> 1.0"
}

provider "aws" {
  region = "eu-central-1"
}