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