locals {
  app_name = "chunker"

  name_prefix = "${var.environment}-${local.app_name}"
  env_vars = {
    PROJECT_ID = var.project_id
  }
}

module "app" {
  source         = "./services/app"
  name_prefix    = "${local.name_prefix}-app"
  image_tag      = var.image_tag
  region         = var.region
  environment    = var.environment
  public         = var.public
  env_vars_plain = local.env_vars
}
