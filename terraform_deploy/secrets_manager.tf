resource "random_password" "fma_secrets_db_pass"{
  length           = 16
  special          = true
  override_special = "_!%^"
}

resource "aws_secretsmanager_secret" "fma_db_secrets_manager" {
  name = local.resource_names.model_data_db_name
}

resource "aws_secretsmanager_secret_version" "password" {
  secret_id = aws_secretsmanager_secret.fma_db_secrets_manager.id
  secret_string = random_password.fma_secrets_db_pass.result
}
