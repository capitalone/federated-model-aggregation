resource aws_lb_target_group api_service_taget_group {
    name                    = "${aws_lambda_function.fma_serverless_api_service.function_name}-tg"
    target_type             = var.api_service_taget_group_defaults["target_type"]
    port                    = var.api_service_taget_group_defaults["port"]
    tags                    = var.tags

    health_check {
        enabled = true
        interval = 35
        path = "/api/v1"
    }
}

resource aws_lambda_permission lambda_target_group_permission {
    statement_id            = var.lambda_target_group_permission_defaults["statement_id"]
    action                  = var.lambda_target_group_permission_defaults["action"]
    function_name           = aws_lambda_function.fma_serverless_api_service.function_name
    principal               = var.lambda_target_group_permission_defaults["principal"]
    source_arn              = aws_lb_target_group.api_service_taget_group.arn
}

resource "aws_lb_target_group_attachment" "tg_to_lambda" {
    target_group_arn        = aws_lb_target_group.api_service_taget_group.arn
    target_id               = aws_lambda_function.fma_serverless_api_service.arn
    depends_on              = [aws_lambda_permission.lambda_target_group_permission]
}
