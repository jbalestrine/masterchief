terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "my-org"
    workspaces {
      name = "tfe-aks-demo"
    }
  }
}
