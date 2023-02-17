# Declaring the Required provider (Docker provider)
terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "2.16.0"
    }
  }
}

provider "docker" {
  host = "tcp://192.168.1.97:2375/"
}
