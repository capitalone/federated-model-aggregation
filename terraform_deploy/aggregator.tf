resource "aws_lambda_function" "fma_serverless_aggregator" {
    filename                              = data.archive_file.zip_aggregator.output_path
    function_name                         = local.resource_names.aggregator_name
    source_code_hash                      = data.archive_file.zip_aggregator.output_base64sha256
    role                                  = local.roles.aggregator_role
    handler                               = "app.handler"
    runtime                               = "python3.9"
    description                           = var.aggregator_defaults["description"]
    reserved_concurrent_executions        = var.aggregator_defaults["reserved_concurrent_executions"]
    timeout                               = var.aggregator_defaults["timeout"]
    memory_size                           = var.aggregator_defaults["memory_size"]
    tags                                  = var.tags

    vpc_config {
        security_group_ids = local.security_groups_ids
        subnet_ids = var.subnet_ids
    }

    environment {
        variables = merge(local.agg_env_vars, local.db_specific_env_vars)
    }

    layers = local.resource_arns.secrets_manager_arns
    depends_on = [
        aws_db_instance.metadata_db,
        aws_s3_bucket.model_data_db
    ]
}
