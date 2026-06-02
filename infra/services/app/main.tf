variable "name_prefix" {
  type = string
}
variable "region" {
  type = string
}
variable "image_tag" {
  type = string
  default = "cpu-0.3.3"
}
variable "public" {
  type    = bool
  default = false
}
variable "environment" {
  type = string
}
variable "env_vars_plain" {
  type = map(string)
}

output "name" {
  value       = try(module.app[0].name, null)
  description = "Cloud Run service name"
}
output "service_url" {
  value       = try(module.app[0].service_url, null)
  description = "Cloud Run service URL"
}
output "run_service_account_email" {
  value       = try(module.app[0].run_service_account_email, null)
  description = "Cloud Run service account email"
}
output "pubsub_topics" {
  value = local.pubsub_topics
}
output "env_vars" {
  value = local.env_vars
}
output "env_file" {
  value = join("\n", concat(
    [
      for key, val in local.env_vars :
      "${key}=\"${val}\""
      if val != null
    ],
    [""]
  ))
}


locals {
  service_name       = "chunker"
  image_name         = "chunker"
  container_registry = "europe-west3-docker.pkg.dev/development-428212/docker-eu"
  pubsub_topics = {
    CHUNKING_REQUESTS_TOPIC = {
      topic_name    = "${local.name_prefix}-chunking-requests"
      push_endpoint = "/pub-sub/requests"
    }
    CHUNK_EMBEDDING_REQUESTS_TOPIC = {
      topic_name    = "${local.name_prefix}-embeddings-requests"
      push_endpoint = "/pub-sub/requests/embeddings"
    }
  }
  pubsub_subscriptions = {
    CHUNKING_REQUESTS_SUBSCRIPTION = "${local.pubsub_topics["CHUNKING_REQUESTS_TOPIC"].topic_name}-sub"
    CHUNK_EMBEDDING_REQUESTS_SUBSCRIPTION = "${local.pubsub_topics["CHUNK_EMBEDDING_REQUESTS_TOPIC"].topic_name}-sub"
  }

  name_prefix     = "${var.name_prefix}"
  container_image = "${local.container_registry}/${local.image_name}:${var.image_tag}"
  create_app      = !contains(["it", "local"], var.environment)
  env_vars = merge(var.env_vars_plain, {
    for key, topic in local.pubsub_topics :
    "${key}" => topic.topic_name
    }, !local.create_app ? {
    for key, sub in local.pubsub_subscriptions :
    "${key}" => sub
  } : {})

}

data "google_project" "current" {
}

module "app" {
  count  = local.create_app ? 1 : 0
  source = "../../modules/cloud_run_service"

  name            = local.name_prefix
  project_id      = data.google_project.current.project_id
  container_image = local.container_image
  region          = var.region
  public          = var.public
  cpu_limit       = "4"
  memory_limit    = "8G"
  env_vars_plain  = local.env_vars
  service_account_roles = [
    "roles/run.invoker",
    "roles/datastore.user",
    "roles/storage.objectUser",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/iam.serviceAccountTokenCreator"
  ]

}


module "pubsub_topics" {
  source   = "../../modules/pubsub-topic-with-dlq"
  for_each = local.pubsub_topics

  project_id               = data.google_project.current.project_id
  environment              = var.environment
  topic_name               = each.value.topic_name
  subscription_name_suffix = local.create_app ? "push" : "sub"
  push_endpoint            = try("${module.app[0].service_url}/${each.value.push_endpoint}", null)
}
