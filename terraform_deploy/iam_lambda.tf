resource "aws_iam_role_policy" "fma_serverless_s3_policy" {
    name = "${var.application_base_name}-s3-policy"
    role = aws_iam_role.fma_serverless_scheduled_role.id
    policy = data.aws_iam_policy_document.s3_access_policy.json
}

resource "aws_iam_role_policy" "fma_serverless_scheduled_policy" {
    name = "${var.application_base_name}-scheduled-policy"
    role = aws_iam_role.fma_serverless_scheduled_role.id
    policy = data.aws_iam_policy_document.scheduling_policy.json
}

resource "aws_iam_role_policy" "fma_serverless_secrects_manager_policy" {
    name = "${var.application_base_name}-secrets-manager"
    role = aws_iam_role.fma_serverless_scheduled_role.id
    policy = data.aws_iam_policy_document.secrets_policy.json
}

resource "aws_iam_role" "fma_serverless_scheduled_role" {
    name = "${var.application_base_name}-scheduled-role"
    assume_role_policy = file("iam/scheduled/dev/trust.json")
    tags = var.tags
}
