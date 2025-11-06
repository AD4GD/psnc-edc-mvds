prod: # make prod p=8000
ifndef p
	uvicorn api.main:app --host 0.0.0.0 --port 8000
endif
	uvicorn api.main:app --host 0.0.0.0 --port "$(p)"

dev: # make dev p=8000
ifndef m
	uvicorn api.main:app --host 0.0.0.0 --reload --port 8000
endif
	uvicorn api.main:app --host 0.0.0.0 --reload --port "$(p)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

migrate:
ifndef m
	$(error Need to correct message, eg. make revision m="add user table")
endif
	alembic revision --autogenerate -m "$(m)"

install-dependencies:
	pip install -r requirements.txt

test:
	pytest -v

shell:
	python
