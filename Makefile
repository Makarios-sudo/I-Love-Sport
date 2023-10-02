# ---------------------------------------------------------------------------------------------------------------------
# Local development commands
# ---------------------------------------------------------------------------------------------------------------------

# Run the local development server
run-local:
	sudo docker-compose -f local.yml down --remove-orphans && sudo docker-compose -f local.yml up --no-build --abort-on-container-exit --remove-orphans && sudo docker-compose -f local.yml down --remove-orphans

run-production:
	docker-compose -f production.yml up --no-build --abort-on-container-exit --remove-orphans

run-local-build:
	make local-down && sudo docker-compose -f local.yml up --build --remove-orphans

run-production-build:
	make production-down && docker-compose -f production.yml up --build --remove-orphans


local-down:
	sudo docker-compose -f local.yml down --remove-orphans


production-down:
	docker-compose -f production.yml down --remove-orphans

build-local:
	sudo docker-compose -f local.yml build

build-production:
	docker-compose -f production.yml build

pre-commit:
	pre-commit run --all-files

# Run tests locally
test-local:
	docker-compose -f local.yml run --rm django sh -c "coverage run -m pytest && coverage report"

# Coverage Report
coverage-report:
	docker-compose -f local.yml run --rm django coverage report

# Execute the makemigrations command
makemigrations:
	sudo docker-compose -f local.yml run --rm django python manage.py makemigrations

makemigrations-merge:
	sudo docker-compose -f local.yml run --rm django python manage.py makemigrations --merge

makemigrations-production:
	docker-compose -f production.yml run --rm django python manage.py makemigrations

collectstatic:
	docker-compose -f local.yml run --rm django python manage.py $@ --no-input

# Execute the custom manage.py run_test command
run_test:
	docker-compose -f local.yml run --rm django python manage.py $@

activate_account:
	docker-compose -f local.yml run --rm django python manage.py $@

# Execute the makemigrations command
merge:
	docker-compose -f local.yml run --rm django python manage.py makemigrations --merge

swagger:
	docker-compose -f local.yml run --rm django python manage.py generate_swagger swagger.json -o -m -u http://localhost:8000

# Execute the migrate command
migrate:
	docker-compose -f local.yml run --rm django python manage.py $@

migrate-production:
	docker-compose -f production.yml run --rm django python manage.py migrate

generatesuperuser:
	docker-compose -f local.yml run --rm django python manage.py $@

migrate-fake:
	docker-compose -f local.yml run --rm django python manage.py migrate --fake

create-superuser:
	sudo docker-compose -f local.yml run --rm django python manage.py createsuperuser


create-new_django-app:
	sudo docker-compose -f local.yml run --rm django python manage.py startapp <appname>


# Run the django shell
shell:
	docker-compose -f local.yml run --rm django python manage.py $@ -i python

shell-production:
	docker-compose -f production.yml run --rm django python manage.py shell -i python


createsuperuser:
	sudo docker-compose -f local.yml run --rm django python manage.py $@

# Run the django shell
bash:
	docker-compose -f local.yml run --rm django $@

migrate-all:
	sudo make makemigrations && sudo make migrate


# Open a shell in the container
bash-local:
	docker-compose -f local.yml run --rm django /bin/bash

# ---------------------------------------------------------------------------------------------------------------------
# Services Commands
# ---------------------------------------------------------------------------------------------------------------------

start-web:
	/start

start-beat:
	/start-celerybeat

start-worker:
	/start-celeryworker

start-flower:
	/start-flower

# volume-down
# 	sudo docker-compose -f local.yml down -v