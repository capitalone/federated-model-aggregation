resource "aws_lb" "api_service_alb" {
    name                              = local.resource_names.api_service_alb_name
    internal                          = var.api_service_alb_defaults["internal"]
    load_balancer_type                = var.api_service_alb_defaults["load_balancer_type"]
    security_groups                   = local.security_groups.api_service_alb_sg_ids
    subnets                           = var.subnet_ids
    enable_deletion_protection        = var.api_service_alb_defaults["enable_deletion_protection"]
    tags                              = var.tags
}

resource "aws_lb_listener" "api_service_listener" {
    load_balancer_arn                 = aws_lb.api_service_alb.arn
    port                              = var.api_service_listeners_defaults["unsecure_port"]
    protocol                          = var.api_service_listeners_defaults["unsecure_protocol"]

    default_action {
        type = "forward"
        target_group_arn = aws_lb_target_group.api_service_taget_group.arn
    }
}

resource "aws_lb_listener" "api_service_listener_secure" {
    load_balancer_arn                 = aws_lb.api_service_alb.arn
    port                              = var.api_service_listeners_defaults["secure_port"]
    protocol                          = var.api_service_listeners_defaults["secure_protocol"]
    ssl_policy                        = var.api_service_listeners_defaults["ssl_policy"]
    certificate_arn                   = var.api_service_listeners_defaults["certificate_arn"]

    default_action {
        type = "forward"
        target_group_arn = aws_lb_target_group.api_service_taget_group.arn
    }
}
