terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.49"
    }
  }
}

variable "aws_region" {
  type = string
}

provider "aws" {
  region  = var.aws_region
}

provider "aws" {
  alias  = "useast1"
  region = "us-east-1"
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

variable "app_ident" {
  description = "Identifier of the application"
  type        = string
}

variable "environment" {
  type        = string
}

variable "current_timestamp" {
  type = string
}
