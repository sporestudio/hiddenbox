# main.terraform

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
    token      = var.aws_session_token
    region     = var.region
}

data "aws_vpc" "default" {
    default = true
}

# Instances deployment
resource "aws_instance" "main" {
    count = var.instances_amount
    ami           = var.ami
    instance_type = var.instance_type
    key_name      = aws_key_pair.main.key_name
    user_data     = var.user
    vpc_security_group_ids = [aws_security_group.main.id]
    associate_public_ip_address = true

    tags = {
        Name = "instance-${count.index}"
    }
}

# Key pair
resource "aws_key_pair" "main" {
    key_name   = "main"
    public_key = file("~/.ssh/id_rsa.pub")
}


# Security group
resource "aws_security_group" "main" {
    vpc_id = data.aws_vpc.default.id

    # SSH access
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
    }


    # Allow all outbound traffic
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = [ "0.0.0.0/0" ]
    }
}