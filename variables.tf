variable "project_name" {
  description = "Project name"
  type = string
  default = "hiddenbox"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type = string
  sensitive = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type = string
  sensitive = true
}

variable "aws_session_token" {
  description = "AWS Session Token"
  type = string
  sensitive = true
}

variable "region" {
  description = "AWS region"
  type = string
  default = "us-east-1"
}

variable "ubuntu_ami" {
  description = "Ubuntu 22.04 AMI ID"
  type        = string
  default     = "ami-0f9575d3d509bae0c"
}

variable "user" {
  description = "The user data to provide when launching the instance"
  type = string
  default = "provisioner"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

variable "main_instance_type" {
  description = "The type of EC2 instance to main node"
  type = string
  default = "t3.medium"
}

variable "storage_instance_type" {
  description = "Instance type for storage nodes"
  type        = string
  default     = "t3.small" 
}

variable "instances_amount" {
  description = "The amount of instances to launch"
  type = number
  default = 3
}

variable "storage_volume_size" {
  description = "Size in GB for each storage node EBS volume"
  type        = number
  default     = 100
}