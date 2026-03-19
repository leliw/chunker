locals {
  service_name    = "chunker"
  container_image = "europe-west3-docker.pkg.dev/development-428212/docker-eu/chunker:gpu-0.3.3"

  name_prefix                 = "${var.environment}-${local.service_name}"
  firestore_prefix = "projects/${local.name_prefix}"
  create_app                  = var.environment != "it" && var.environment != "local"
}

resource "google_cloud_run_v2_service" "app" {
  count               = local.create_app ? 1 : 0
  name                = "${local.name_prefix}-run"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = var.environment != "prod"

  scaling {
    min_instance_count = 0
  }

  template {
    containers {
      image = local.container_image

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_ROOT_STORAGE"
        value = local.firestore_prefix
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    service_account = var.run_service_account_email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].labels,
      template[0].annotations,
    ]
  }
}


module "pubsub_chunking_requests" {
  source                     = "./modules/pubsub-topic-with-dlq"
  project_id                 = var.project_id
  environment                = var.environment
  topic_name                 = "${local.name_prefix}-chunking-requests"
  push_endpoint              = try("${google_cloud_run_v2_service.app[0].uri}/pub-sub", null)
  push_service_account_email = var.run_service_account_email
}

module "pubsub_chunking_responses" {
  source                     = "./modules/pubsub-topic-with-dlq"
  project_id                 = var.project_id
  environment                = var.environment
  topic_name                 = "${local.name_prefix}-chunking-responses"
  push_endpoint              = try("${google_cloud_run_v2_service.app[0].uri}/pub-sub", null)
  push_service_account_email = var.run_service_account_email
}

module "pubsub_embeddings_requests" {
  source                     = "./modules/pubsub-topic-with-dlq"
  project_id                 = var.project_id
  environment                = var.environment
  topic_name                 = "${local.name_prefix}-embeddings-requests"
  push_endpoint              = try("${google_cloud_run_v2_service.app[0].uri}/pub-sub", null)
  push_service_account_email = var.run_service_account_email
}



resource "google_service_account" "test_runner" {
  count        = local.create_app ? 1 : 0
  account_id   = "test-runner"
  display_name = "Integration test runner"
}

resource "google_project_iam_member" "test_storage" {
  count   = local.create_app ? 1 : 0
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.test_runner[0].email}"
}

resource "google_project_iam_member" "test_pubsub" {
  count   = local.create_app ? 1 : 0
  project = var.project_id
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${google_service_account.test_runner[0].email}"
}

resource "google_project_iam_member" "test_token_creator" {
  count   = local.create_app ? 1 : 0
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.test_runner[0].email}"
}

resource "google_project_iam_member" "service_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${var.run_service_account_email}"
}

resource "google_project_iam_member" "service_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.admin"
  member  = "serviceAccount:${var.run_service_account_email}"
}

resource "google_project_iam_member" "service_token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${var.run_service_account_email}"
}

