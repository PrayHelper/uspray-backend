build-dev:
	docker compose -p backend-dev -f ./deploy/docker-compose.dev.yml down
	docker compose -p backend-dev -f ./deploy/docker-compose.dev.yml up --build -d

build-prod:
	docker compose -p backend-prod -f ./deploy/docker-compose.prod.yml up --build -d

build-intg:
	docker compose -p backend-intg -f ./deploy/docker-compose.intg.yml down
	docker compose -p backend-intg -f ./deploy/docker-compose.intg.yml up --build -d