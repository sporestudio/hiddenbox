# main.terraform

terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
        }
    }

    backend "s3" {
        bucket = "tfstate-hiddenbox"
        key    = "terraform.tfstate"
        region = "us-east-1"
        encrypt = true
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


# Security group for storage modules
resource "aws_security_group" "storage_nodes" {
    name = "storage_nodes_sg"
    description = "Security group for storage nodes"
    vpc_id = data.aws_vpc.default.id

    # SSH Access
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow SSH access"
    }

    # API Access
    ingress {
        from_port   = 8080
        to_port     = 8080
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow API access"
    }

    # Kubernetes API
    ingress {
        from_port   = 6443
        to_port     = 6443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow Kubernetes API access"
    }


    # Allow all internal communication between nodes
    ingress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        self = true
        description = "Allow all internal communication"
    }

    # Allow all outbound traffic
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "storage-nodes-sg"
        Project = "hiddenbox"
    }
}


# Security group
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

    # PostgreSQL access
    ingress {
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
        self = true
        description = "Allow PostgreSQL access"
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


# Key pair
resource "aws_key_pair" "main" {
    key_name   = "main"
    public_key = file(var.ssh_public_key_path)
}


# EBS volumes for storage nodes
resource "aws_ebs_volume" "storage_volume" {
    count               = var.instances_amount
    availability_zone   = element(aws_instance.storage[*].availability_zone, count.index)
    size                = var.storage_volume_size
    type                = "gp3"
    encrypted           = true

    tags = {
        Name = "storage-volume-${count.index}"
        Project = "hiddenbox"
    }
}


# Main instance used to API, database and other services
resource "aws_instance" "main" {
    count                   = var.instances_amount
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


# Instances for storage nodes
resource "aws_instance" "storage" {
    count                   = var.instances_amount
    ami                     = var.ubuntu_ami
    instance_type           = var.storage_instance_type
    key_name                = aws_key_pair.main.key_name
    user_data               = var.user
    vpc_security_group_ids  = [aws_security_group.storage_nodes.id]
    associate_public_ip_address = true

    root_block_device {
        volume_size = 20
        volume_type = "gp3"
    }

    tags = {
        Name = "storage-node-${count.index}"
        Project = "hiddenbox"
        Role = "storage"
    }
}


# Associate EBS volumes with storage nodes
resource "aws_volume_attachment" "storage" {
    count       = var.instances_amount
    device_name = "/dev/sdf"
    volume_id   = element(aws_ebs_volume.storage_volume[*].id, count.index)
    instance_id = element(aws_instance.storage[*].id, count.index)
}


# Output the public IP addresses of the instances
output "main_public_ip" {
    value = aws_instance.main[0].public_ip
    description = "The public IP address of the main node"
}

output "storage_public_ip" {
    value = aws_instance.storage[*].public_ip
    description = "The public IP address of the storage nodes"
}


# Generate inventory.ini file for Ansible
resource "local_file" "ansible_inventory" {
    content = templatefile("templates/inventory.tpl", {
        main_ip = aws_instance.main[0].public_ip,
        storage_ips = aws_instance.storage[*].public_ip
    })
    filename = "inventory.ini"
}