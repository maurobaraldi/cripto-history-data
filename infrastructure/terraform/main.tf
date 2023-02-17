resource "docker_image" "rabbitmq" {               
  name = "rabbitmq:3.11-management"
}

resource "docker_container" "message-broker" {   
  image = docker_image.rabbitmq.name
  name = "message-broker"
  # networks_advanced {
  #   name    = docker_network.rabbitmq.name
  #   aliases = ["rabbitmq"]
  # }
  attach = false
  must_run = true
  rm = true
  ports {
    internal = 15672
    external = 15672
    ip = "0.0.0.0"
  }
  ports {
    internal = 5672
    external = 5672
    ip = "0.0.0.0"
  }
}

resource "docker_image" "postgres" {               
  name = "postgres:alpine"
}

resource "docker_volume" "postgres" {
  name = "postgres"
}

resource "docker_container" "database" {   
  image = docker_image.postgres.name
  name = "database"
  attach = false
  must_run = true
  rm = true
  ports {
    internal = 5432
    external = 5432
    ip = "0.0.0.0"
  }
  env = [
    "POSTGRES_PASSWORD=x",
  ]
  volumes {
    container_path  = "/var/data/"
    host_path = "/var/data/"
    read_only = false
    volume_name = "${docker_volume.postgres.name}"
  }
}

resource "docker_service" "registry" {
  name = "registry"

  task_spec {
    container_spec {
      image = "registry:2"
    }
  }

  endpoint_spec {
    ports {
      published_port = "5000"
      target_port = "5000"
    }
  }
}
