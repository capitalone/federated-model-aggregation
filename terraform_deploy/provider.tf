provider "aws" {
    region                   = var.provider_defaults.region
    shared_credentials_files = var.shared_credentials_files_default
    profile                  = var.provider_defaults.profile
}
