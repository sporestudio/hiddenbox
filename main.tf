terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
        }
    }

    backend "local" {
        path = "terraform.tfstate"
    }
}

provider "aws" {
    shared_credentials_files = [ "~/.aws/credentials" ]
    region = var.region
}

data "aws_vpc" "default" {
    default = true
}

resource "random_id" "bucket_suffix" {
    byte_length = 4
}

# S3 main bucket
resource "aws_s3_bucket" "main_storage" {
    bucket = "${var.project_name}-main-storage"
    force_destroy = true

    tags = {
        Name = "main storage"
        Project = var.project_name
        Environment = "production"
    }
}

# Versioning main storage
resource "aws_s3_bucket_versioning" "main_versioning" {
    bucket = aws_s3_bucket.main_storage.id
    versioning_configuration {
        status = "Enabled"
    }
}

# Cipher configuration for main bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "main_encryption" {
    bucket = aws_s3_bucket.main_storage.id

    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "AES256"
        }
    }
}

# Block public access to main bucket
resource "aws_s3_bucket_public_access_block" "main_block_access" {
    bucket = aws_s3_bucket.main_storage.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

}

# Security group for main node
resource "aws_security_group" "main" {
    name = "main_node_sg"
    description = "Security group for main node"
    vpc_id = data.aws_vpc.default.id

    # SSH access
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = [ "0.0.0.0/0" ]
        description = "Allow SSH access"
    }

    # Web frontend
    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = [ "0.0.0.0/0"]
        description = "Allow HTTP access"
    }

    # HTTPS access
    ingress {
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = [ "0.0.0.0/0"]
        description = "Allow HTTPS access"
    }

    # Allow all outbound traffic
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = [ "0.0.0.0/0" ]
    }

    tags = {
        Name = "main-node-sg"
        Project = "hiddenbox"
    }
}

# Key pair for SSH access
resource "aws_key_pair" "main" {
    key_name   = "main"
    public_key = file(var.ssh_public_key_path)
}

# Main instance used to API, database and other services
resource "aws_instance" "main" {
    ami                     = var.ubuntu_ami
    instance_type           = var.main_instance_type
    key_name                = aws_key_pair.main.key_name
    user_data               = var.user
    vpc_security_group_ids  = [aws_security_group.main.id]
    associate_public_ip_address = true

    root_block_device {
        volume_size = 30
        volume_type = "gp3"
    }

    tags = {
        Name = "main-node"
        Project = "hiddenbox"
        Role = "api-db-ochestrator"
    }
}
