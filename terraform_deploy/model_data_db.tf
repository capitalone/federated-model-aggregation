resource "aws_s3_bucket_policy" "allow_access_to_metadata_db" {
  bucket = aws_s3_bucket.model_data_db.id
  policy = data.aws_iam_policy_document.s3_access_policy.json
    
    depends_on = [
        aws_iam_role.fma_serverless_scheduled_role
    ]
}

resource "aws_s3_bucket" "model_data_db" {
    bucket                              = local.resource_names.model_data_db_name
    tags                                = var.tags

    server_side_encryption_configuration {
        rule {
            apply_server_side_encryption_by_default {
                kms_master_key_id = aws_kms_key.model_data_db_kms_key.arn
                sse_algorithm     = var.model_data_db_defaults["sse_algorithm"]
            }
        }
    }
}

resource "aws_s3_bucket_acl" "model_data_db_acl" {
    bucket                             = aws_s3_bucket.model_data_db.id
    acl                                = var.model_data_db_defaults["main_acl"]
}

resource "aws_s3_bucket_versioning" "model_data_db_versioning" {
    bucket                             = aws_s3_bucket.model_data_db.id

    versioning_configuration {
        status = var.model_data_db_defaults["versiong_config_status"]
    }
}

resource "aws_kms_key" "model_data_db_kms_key" {
    description                       = var.model_data_db_defaults["kms_key_description"]
    deletion_window_in_days           = 10
}

resource "aws_s3_bucket" "model_data_db_log_bucket" {
    bucket                           = local.resource_names.model_data_log_db_name
}

resource "aws_s3_bucket_acl" "model_data_db_log_bucket_acl" {
    bucket                          = aws_s3_bucket.model_data_db_log_bucket.id
    acl                             = var.model_data_db_defaults["log_acl"]
}

resource "aws_s3_bucket_logging" "model_data_db_log_bucket_link" {
    bucket                          = aws_s3_bucket.model_data_db.id
    target_bucket                   = aws_s3_bucket.model_data_db_log_bucket.id
    target_prefix                   = var.model_data_db_defaults["log_target_prefix"]
}
