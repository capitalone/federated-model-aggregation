data "aws_secretsmanager_secret" "local_path_to_password" {
  name = local.resource_names.model_data_db_name
}

data "aws_secretsmanager_secret_version" "password" {
  secret_id = data.aws_secretsmanager_secret.local_path_to_password
}

resource "aws_db_parameter_group" "metadata_db_parameter_group" {
    count  = var.metadata_db_parameters == [] ? 1 : 0
    name   = local.resource_names.metadata_db_parameter_group_name
    family = local.db_parameter_family

    dynamic "parameter" {
        for_each = var.metadata_db_parameters
        content {
            name         = parameter.value.name
            value        = parameter.value.value
        }
    }
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
    parameter_group_name                      = length(aws_db_parameter_group.metadata_db_parameter_group) == 1 ? aws_db_parameter_group.metadata_db_parameter_group[length(aws_db_parameter_group.metadata_db_parameter_group)].name: ""
    skip_final_snapshot                       = var.metadata_db_defaults["skip_final_snapshot"]
    availability_zone                         = var.metadata_db_defaults["availability_zone"]
    iam_database_authentication_enabled       = var.metadata_db_defaults["iam_database_authentication_enabled"]
    port                                      = var.metadata_db_defaults["port"]
    storage_encrypted                         = var.metadata_db_defaults["storage_encrypted"]
    db_subnet_group_name                      = var.metadata_db_defaults["db_subnet_group_name"]
    tags                                      = merge(var.tags, local.metadata_db_tags)
    vpc_security_group_ids                    = local.security_groups.metadata_db_sg_ids
    identifier                                = local.resource_names.metadata_db_identifier
    copy_tags_to_snapshot                     = true

    enabled_cloudwatch_logs_exports = [
        "postgresql",
        "upgrade",
    ]
}
