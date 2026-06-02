output "service_url" {
  value       = try(module.app.service_url, null)
  description = "Publiczny URL usługi Cloud Run"
}
output "CHUNKING_REQUESTS_TOPIC" {
  value=module.app.pubsub_topics["CHUNKING_REQUESTS_TOPIC"].topic_name
}
output "env_vars" {
  value = local.env_vars
}
output "env_vars_file" {
  value = join("\n", concat(
    [
      for key, val in local.env_vars :
      "${key}=\"${val}\""
      if val != null
    ], [""]
  ))
}
