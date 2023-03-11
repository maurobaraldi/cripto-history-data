#export DOCKER_HOST=tcp://ubuntu@192.168.1.97

provision-plan:
	terraform -chdir=infrastructure/terraform plan

provision-apply:
	terraform -chdir=infrastructure/terraform apply

deploy-worker:
	docker-compose up -d

down-worker:
	docker-compose down

build-local-env:
	# DB Service - PostgreSQL 
	#docker run -d --rm --name pgtest -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:alpine

	# Message Queue Service - Rabbit MQ
	#docker run -d --rm --hostname my-rabbit --name rmqtest rabbitmq:alpine

	# Init Database
	python3 -c "from tasks.common import initdb; initdb()"
 
build-worker:
	docker-compose build worker



