variable "name" {
  type        = string
  description = "Service name"
}
variable "container_image" {
  type        = string
  description = "Container image"
}
variable "image_registry" {
  type        = string
  default     = null
  description = "Container image registry (required for otelcol sidecar)"
}
variable "env_vars_plain" {
  type        = map(string)
  default     = {}
  description = "Environment variables - plain strings"
}
variable "env_vars_secrets" {
  type        = map(string)
  default     = {}
  description = "Environment variables - secrets from Secret Manager"
}
variable "region" {
  type    = string
  default = "europe-west1"
}
variable "project_id" {
  type = string
}
variable "public" {
  type    = bool
  default = false
}
variable "deletion_protection" {
  type    = bool
  default = false
}
variable "cpu_limit" {
  type    = string
  default = "0.5"
}
variable "memory_limit" {
  type    = string
  default = "512Mi"
}
variable "min_instances" {
  type    = number
  default = 0
}
variable "max_instances" {
  type    = number
  default = 10
}

# === Service Account ===

variable "run_service_account_email" {
  description = "Email istniejącego Service Accounta. Jeśli null -> zostanie stworzony."
  type        = string
  default     = null
}

variable "service_account_roles" {
  description = "Role, które mają być nadane Service Accountowi"
  type        = list(string)
  default = [
    "roles/run.invoker",
    "roles/datastore.user",
    "roles/storage.objectUser",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/iam.serviceAccountTokenCreator",
    "roles/logging.logWriter",           # Logi
    "roles/monitoring.metricWriter",     # Metryki
    "roles/cloudtrace.agent",            # Trace'y
    "roles/secretmanager.secretAccessor" # Sekrety
  ]
}

variable "terraform_runner_member" {
  description = "Tożsamość, która uruchamia Terraform (potrzebna do iam.serviceAccountUser)"
  type        = string
  default     = null # jeśli null -> użyj CURRENT_PROJECT_NUMBER-compute@developer.gserviceaccount.com
}
