resource "aws_lambda_function" "fma_serverless_api_service" {
    filename                              = data.archive_file.zip_api_service.output_path
    function_name                         = local.resource_names.api_service_name
    source_code_hash                      = data.archive_file.zip_api_service.output_base64sha256
    role                                  = local.roles.api_service_role
    handler                               = "service_initialization.handler"
    runtime                               = "python3.9"
    description                           = var.api_service_defaults["description"]
    reserved_concurrent_executions        = var.api_service_defaults["reserved_concurrent_executions"]
    timeout                               = var.api_service_defaults["timeout"]
    memory_size                           = var.api_service_defaults["memory_size"]
    tags                                  = var.tags
    publish                               = true

    vpc_config {
        security_group_ids = local.security_groups.api_service_sg_ids
        subnet_ids = var.subnet_ids
    }

    environment {
        variables = merge(local.api_env_vars, local.db_specific_env_vars)
    }

    layers = local.resource_arns.secrets_manager_arns
    depends_on = [
        aws_db_instance.metadata_db,
        aws_s3_bucket.model_data_db
    ]
}
