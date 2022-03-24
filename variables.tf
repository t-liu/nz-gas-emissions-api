variable "tf_cloud_org_name" {
  description = "Terraform Cloud Organization Name"
  type        = string
  default     = "t-liu-production"
}
variable "tf_cloud_ws_name" {
  description = "Terraform Cloud Workspace Name"
  type        = string
  default     = "nz-gas-emissions-api"
}
variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}