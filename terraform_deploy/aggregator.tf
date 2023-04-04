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
    publish                               = true

    vpc_config {
        security_group_ids = local.security_groups.aggregator_sg_ids
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


resource "aws_lambda_alias" "fma_serverless_aggregator_alias" {
  name             = local.resource_names.aggregator_alias_name
  function_name    = aws_lambda_function.fma_serverless_aggregator.arn
  function_version = "$LATEST"
}

resource "aws_lambda_permission" "allow_event_bridge_execution" {
    statement_id  = "AllowExecutionFromEventBridge"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.fma_serverless_aggregator.function_name
    principal     = "events.amazonaws.com"
    source_arn    = local.event_bridge_rule_source_arn
    qualifier     = aws_lambda_alias.fma_serverless_aggregator_alias.name
}
