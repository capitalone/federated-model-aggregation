# SG resource definitions
resource "aws_security_group" "lambda_agg_sg" {
    name        = "${var.application_base_name}-lambda-agg-sg"
    description = "Security Group for the Aggregator Lambda"
    vpc_id      = local.vpc_id
    tags        = var.tags
}

resource "aws_security_group" "alb_sg" {
    name        = "${var.application_base_name}-alb-sg"
    description = "Security Group for the ALB"
    vpc_id      = local.vpc_id
    tags        = var.tags
}

resource "aws_security_group" "lambda_api_sg" {
    name        = "${var.application_base_name}-lambda-api-sg"
    description = "Security Group for the API Lamdba"
    vpc_id      = local.vpc_id
    tags        = var.tags
}

resource "aws_security_group" "rds_sg" {
    name        = "${var.application_base_name}-rds-sg"
    description = "Security Group for the RDS"
    vpc_id      = local.vpc_id
    tags        = var.tags
}

# Inbound/Outbound SG rules for alb to lambda_api
resource "aws_security_group_rule" "alb_to_lambda_api_outbound_sg_rule" {
  type              = "egress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.alb_sg.id
  source_security_group_id = aws_security_group.lambda_api_sg.id
}

resource "aws_security_group_rule" "alb_to_lambda_api_inbound_sg_rule" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.lambda_api_sg.id
  source_security_group_id = aws_security_group.alb_sg.id
}

# Inbound/Outbound SG rules for lambda_api to rds
resource "aws_security_group_rule" "lambda_api_to_rds_outbound_sg_rule" {
  type              = "egress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.lambda_api_sg.id
  source_security_group_id = aws_security_group.rds_sg.id
}

resource "aws_security_group_rule" "lambda_api_to_rds_inbound_sg_rule" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.rds_sg.id
  source_security_group_id = aws_security_group.lambda_api_sg.id
}

# Inbound/Outbound SG rules for lambda_agg to rds
resource "aws_security_group_rule" "lambda_agg_to_rds_outbound_sg_rule" {
  type              = "egress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.lambda_agg_sg.id
  source_security_group_id = aws_security_group.rds_sg.id
}

resource "aws_security_group_rule" "lambda_agg_to_rds_inbound_sg_rule" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  security_group_id = aws_security_group.rds_sg.id
  source_security_group_id = aws_security_group.lambda_agg_sg.id
}
