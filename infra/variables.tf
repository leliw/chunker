variable "environment" {
  type = string
}
variable "project_id" {
  type = string
}
variable "image_tag" {
  type = string
  default = "cpu-0.3.3"
}
variable "region" {
  type    = string
  default = "europe-west1"
}
variable "run_service_account_email" {
  type = string
  default = null
}
variable "public" {
  type    = bool
  default = false
}
variable "min_instances" {
  type    = number
  default = 0
}
variable "max_instances" {
  type    = number
  default = 10
}

