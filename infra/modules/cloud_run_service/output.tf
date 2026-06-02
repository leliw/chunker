output "service_url" {
  value       = try(google_cloud_run_v2_service.app.uri, null)
  description = "Cloud Run service URL"
}
output "name" {
  value       = try(google_cloud_run_v2_service.app.name, null)
  description = "Cloud Run service name"
}
output "run_service_account_email" {
  value       = local.create_service_account ? google_service_account.app[0].email : var.run_service_account_email
  description = "Cloud Run service account email"
}
