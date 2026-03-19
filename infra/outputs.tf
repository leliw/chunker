output "service_url" {
  value       = try(google_cloud_run_v2_service.app[0].uri, null)
  description = "Publiczny URL usługi Cloud Run"
}

output "CHUNKING_REQUESTS_SUBSCRIPTION" {
  value = module.pubsub_chunking_requests.subscription_name
}

output "CHUNK_EMBEDDING_REQUESTS_TOPIC" {
  value = module.pubsub_embeddings_requests.topic_name
}

output "CHUNK_EMBEDDING_REQUESTS_SUBSCRIPTION" {
  value = local.create_app ? null : module.pubsub_embeddings_requests.subscription_name
}

output "test_runner" {
  value = try(google_service_account.test_runner[0].email, null)
}
