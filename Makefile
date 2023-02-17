export DOCKER_HOST=tcp://ubuntu@192.168.1.97

provision-plan:
	terraform -chdir=infrastructure/terraform plan

provision-apply:
	terraform -chdir=infrastructure/terraform apply

deploy-worker:
	docker-compose up -d

down-worker:
	docker-compose down
