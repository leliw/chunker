variable "environment" {
  type = string
}
variable "project_id" {
  type = string
}
variable "region" {
  type    = string
  default = "europe-west1"
}
variable "run_service_account_email" {
  type = string
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

