data "archive_file" "zip_aggregator" {
    type        = "zip"
    source_dir  = "../aggregator/.aws-sam/build/FmaServerless"
    output_path = "./python/aggregator.zip"
    depends_on  = [random_string.zip_file_update_tag]
    excludes    = ["terraform_deploy"]
}

data "archive_file" "zip_api_service" {
    type        = "zip"
    source_dir  = "../api_service/.aws-sam/build/FmaServerless"
    output_path = "./python/api-service.zip"
    depends_on  = [random_string.zip_file_update_tag]
    excludes    = ["terraform_deploy"]
}

resource "random_string" "zip_file_update_tag" {
  length        = 16
  special       = false
}
