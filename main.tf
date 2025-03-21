# main.terraform {

terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
        }
    }
}

provider "aws" {
    access_key = var.aws_access_key_id
    secret_key = var.aws_secret_access_key
    region     = var.region
    token      = var.aws_session_token
}