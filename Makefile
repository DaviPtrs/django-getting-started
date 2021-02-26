.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := all

## Docker tasks: ##

all: down up

up:
	docker-compose up -d

down:
	docker-compose down

down-v:
	docker-compose down -v

down-all:
	docker-compose down -v --rmi all

build:
	docker-compose build

access:
	docker-compose exec web bash

reload:
	docker-compose restart web

logs:
	docker-compose logs -f web

logs-all:
	docker-compose logs -f

migrations:
	docker-compose exec web python manage.py makemigrations

migrate:
	docker-compose exec web python manage.py migrate

shell:
	docker-compose exec web python manage.py shell

perm:
	sudo chown -R "$USER":"$USER" .