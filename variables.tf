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
  default = "us-west-2"
}

variable "ami" {
  description = "The AMI to use for the instance"
  type = string
  default = "ami-0c55b159cbfafe1f0"
}

variable "user" {
  description = "The user data to provide when launching the instance"
  type = string
  default = "provisioner"
}

variable "instance_type" {
  description = "The type of EC2 instance to launch"
  type = string
  default = "t3.micro"
}

variable "instances_amount" {
  description = "The amount of instances to launch"
  type = number
  default = 3
}