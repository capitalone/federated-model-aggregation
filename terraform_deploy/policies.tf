data "aws_iam_policy_document" "s3_access_policy" {
  statement {
    sid = "DenyAccessForAllExceptFMALambdas"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    effect = "Deny"

    actions = ["s3:*"]

    resources = [
          "arn:aws:s3:::{var.application_base_name}-storage",
          "arn:aws:s3:::{var.application_base_name}-storage/*"
    ]
    condition {
        test     = "StringNotLike"
        variable = "aws:arn"
        values   = [aws_iam_role.fma_serverless_scheduled_role.arn]
    }
  }
}

data "aws_iam_policy_document" "logging_policy" {
    statement {
        sid = "AllowNetorkModsForLambda"
        effect = "Allow"
        resources = ["*"]
        actions = [
            "ec2:CreateNetworkInterface",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DeleteNetworkInterface"
        ]
    }
    statement {
        sid = "AllowCreateLogsLambda"
        effect = "Allow"
        resources = [
            aws_lambda_function.fma_serverless_api_service.arn,
            aws_lambda_function.fma_serverless_aggregator.arn
        ]
        actions = [
                "logs:CreateLogGroup",
                "logs:DescribeLogStreams",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
        ]
    }
}
data "aws_iam_policy_document" "secrets_policy" {
    statement {
        sid = "AllowSecretManagerAccessAndModificationForLambda"
        effect = "Allow"
        resources = [
            aws_lambda_function.fma_serverless_api_service.arn,
            aws_lambda_function.fma_serverless_aggregator.arn
        ]
        actions = [
            "secretsmanager:GetSecretValue"
        ]
    }
}
data "aws_iam_policy_document" "scheduling_policy" {
    statement {
        sid = "AllowScheduledRuleForAggregationLambda"
        effect = "Allow"
        resources = [
            aws_lambda_function.fma_serverless_api_service.arn,
        ]
        actions = [
            "events:DescribeRule",
            "events:DisableRule",
            "events:EnableRule",
            "events:DeleteRule"
        ]
    }
    statement {
        sid = "AllowPutRuleForAggregationLambda"
        effect = "Allow"
        resources = [
            aws_lambda_function.fma_serverless_api_service.arn,
        ]
        actions = [
            "events:PutRule",
            "events:PutTargets",
            "events:TagResource"
        ]
        condition {
            test     = "ForAllValues:ArnEquals"
            variable = "events:TargetArn"
            values   = [aws_iam_role.fma_serverless_scheduled_role.arn]
        }
    }
}
