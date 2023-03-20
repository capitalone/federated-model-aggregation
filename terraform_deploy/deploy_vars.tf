variable "application_base_name" {
    type = string
    default = "fma-serverless"
}

# Deployment defaults for Provider
variable "provider_defaults" {
    type = map
    default = {
        region                   = "<insert region here>"
        profile                  = "<Insert profile name here>"
    }
}
variable "shared_credentials_files_default" {
    type = list
    default = ["<insert path to aws credentials here>"]
}

# Deployment defaults for model data database
variable "model_data_db_defaults" {
    type = map
    default = {
        sse_algorithm                       = "aws:kms"
        main_acl                            = "private"
        versiong_config_status              = "Enabled"
        kms_key_description                 = "This key is used to encrypt bucket objects"
        log_acl                             = "log-delivery-write"
        log_target_prefix                   = "log/"
    }
}

# Deployment defaults for aggregator
variable "aggregator_defaults" {
    type = map
    default = {
        description                         = "Lambda function for fma-serverless aggregator"
        reserved_concurrent_executions      = 10
        timeout                             = 30
        memory_size                         = 256
    }
}

# Deployment defaults for api service
variable "api_service_defaults" {
    type = map
    default = {
        description                         = "Lambda function for fma-serverless api service"
        reserved_concurrent_executions      = 10
        timeout                             = 300
        memory_size                         = 256
    }
}

# Deployment defaults for api service's alb
variable "api_service_alb_defaults" {
    type = map
    default = {
        internal                            = true
        load_balancer_type                  = "application"
        enable_deletion_protection          = false
    }
}

# Deployment defaults for api service's alb listeners
variable "api_service_listeners_defaults" {
    type = map
    default = {
        unsecure_port                       = "80"
        unsecure_protocol                   = "HTTP"
        secure_port                         = "443"
        secure_protocol                     = "HTTPS"
        ssl_policy                          = "<insert ssl policy>"
        certificate_arn                     = "<insert cert arn>"
    }
}
# Deployment defaults for api service's target groups
variable "api_service_taget_group_defaults" {
    type = map
    default = {
        target_type                         = "lambda"
        port                                = 443
    }
}

# Deployment defaults for api service's target group permissions
variable "lambda_target_group_permission_defaults" {
    type = map
    default = {
        statement_id                        = "AllowExecutionFromALB"
        action                              = "lambda:InvokeFunction"
        principal                           = "elasticloadbalancing.amazonaws.com"
    }
}

# Deployment defaults for metadata database
variable "metadata_db_defaults" {
    type = map
    default = {
        allocated_storage                       = 20
        max_allocated_storage                   = 1000
        engine                                  = "postgres"
        engine_version                          = "14.3"
        instance_class                          = "db.t4g.micro"
        username                                = "username"
        parameter_group_name                    = "<insert parameter group name>"
        skip_final_snapshot                     = true
        availability_zone                       = "<insert AZ>"
        iam_database_authentication_enabled     = true
        port                                    = "5432"
        storage_encrypted                       = true
        db_subnet_group_name                    = "<insert subgroup name>"
    }
}

# General reuse variables
variable "tags" {
    type = map
    default = {}
}

variable "subnet_ids" {
    type = list
    default = []
}

locals {
    roles = {
        aggregator_role     = aws_iam_role.fma_serverless_scheduled_role.arn
        api_service_role    = aws_iam_role.fma_serverless_scheduled_role.arn
    }
    resource_arns = {
        secrets_manager_arns = [aws_secretsmanager_secret.fma_db_secrets_manager.arn]
    }
    resource_names = {
        metadata_db_name = "${var.application_base_name}-metadata-database"
        api_service_name = "${var.application_base_name}-api-service"
        aggregator_name = "${var.application_base_name}-aggregator"
        model_data_db_name = "${var.application_base_name}-model-storage"
        db_secrets_manager_name = "${var.application_base_name}-db-password"
        model_data_log_db_name = "${var.application_base_name}-model-storage-log"
        api_service_alb_name = "${var.application_base_name}-api-service-alb"
        metadata_db_identifier = "${var.application_base_name}-metadata-storage"
        metadata_db_parameter_group_name = "${var.application_base_name}-metadata-db-param-group"
        aggregator_alias_name = "${var.application_base_name}-aggregator-alias"
    }
    db_specific_env_vars = {
        FMA_DATABASE_NAME                       = local.resource_names.metadata_db_name
        FMA_DATABASE_HOST                       = aws_db_instance.metadata_db.address
        FMA_DATABASE_PORT                       = "5432"
        FMA_DB_SECRET_PATH                      = "<insert path to secrets here>"
    }
    agg_env_vars = {
        ENV                                     = "dev"
        DJANGO_SETTINGS_MODULE                  = "federated_learning_project.settings_remote"
        PARAMETERS_SECRETS_EXTENSION_HTTP_PORT  = "2773"
        FMA_DATABASE_NAME                       = local.resource_names.metadata_db_name
        FMA_DATABASE_HOST                       = aws_db_instance.metadata_db.address
        FMA_DATABASE_PORT                       = "5432"
        FMA_DB_SECRET_PATH                      = "<insert path to secrets here>"
        FMA_SETTINGS_MODULE                     = "federated_learning_project.fma_settings"
    }
    api_env_vars = {
        ENV                                     = "dev"
        DJANGO_SETTINGS_MODULE                  = "federated_learning_project.settings_remote"
        FMA_DATABASE_NAME                       = local.resource_names.metadata_db_name
        FMA_DATABASE_HOST                       = aws_db_instance.metadata_db.address
        FMA_DATABASE_PORT                       = "5432"
        LAMBDA_INVOKED_FUNCTION_ARN             = aws_lambda_function.fma_serverless_aggregator.arn
        FMA_DB_SECRET_PATH                      = "<insert path to secrets here>"
        PARAMETERS_SECRETS_EXTENSION_HTTP_PORT  = "2773"
        FMA_SETTINGS_MODULE                     = "federated_learning_project.fma_settings"

    }
    security_groups  = {
        aggregator_sg_ids       = [aws_security_group.lambda_agg_sg]
        api_service_sg_ids      = [aws_security_group.lambda_api_sg]
        api_service_alb_sg_ids  = [aws_security_group.alb_sg]
        metadata_db_sg_ids      = [aws_security_group.rds_sg]
    }
    metadata_db_tags = {tags = "<insert metadata db specific tags>"}
    vpc_id = "<insert vpc id>"
    db_parameter_family = "postgres14"
    db_password = data.aws_secretsmanager_secret_version.password
    event_bridge_rule_source_arn = "<insert base arn path for event bridge rule>/fma-scheduled-model-*-dev"

}
