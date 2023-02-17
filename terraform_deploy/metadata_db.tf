data "aws_secretsmanager_secret" "local_path_to_password" {
  name = local.resource_names.model_data_db_name
}

data "aws_secretsmanager_secret_version" "password" {
  secret_id = data.aws_secretsmanager_secret.local_path_to_password
}

resource "aws_db_instance" "metadata_db" {
    allocated_storage                         = var.metadata_db_defaults["allocated_storage"]
    max_allocated_storage                     = var.metadata_db_defaults["max_allocated_storage"]
    db_name                                   = replace("${local.resource_names.metadata_db_name}", "-", "_")
    engine                                    = var.metadata_db_defaults["engine"]
    engine_version                            = var.metadata_db_defaults["engine_version"]
    instance_class                            = var.metadata_db_defaults["instance_class"]
    username                                  = var.metadata_db_defaults["username"]
    password                                  = local.db_password
    parameter_group_name                      = var.metadata_db_defaults["parameter_group_name"]
    skip_final_snapshot                       = var.metadata_db_defaults["skip_final_snapshot"]
    availability_zone                         = var.metadata_db_defaults["availability_zone"]
    iam_database_authentication_enabled       = var.metadata_db_defaults["iam_database_authentication_enabled"]
    port                                      = var.metadata_db_defaults["port"]
    storage_encrypted                         = var.metadata_db_defaults["storage_encrypted"]
    db_subnet_group_name                      = var.metadata_db_defaults["db_subnet_group_name"]
    tags                                      = var.tags
    vpc_security_group_ids                    = var.vpc_security_group_ids
    identifier                                = local.resource_names.metadata_db_identifier
}
