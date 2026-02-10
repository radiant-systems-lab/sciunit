terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

# Lambda@Edge must be deployed in us-east-1
provider "aws" {
  region  = "us-east-1"
  profile = var.aws_profile
}
