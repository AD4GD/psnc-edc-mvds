prod: # make prod p=8000
ifndef p
	uvicorn main:app --host 0.0.0.0 --port 5555
endif
	uvicorn main:app --host 0.0.0.0 --port "$(p)"

dev: # make dev p=8000
ifndef m
	uvicorn main:app --host 0.0.0.0 --reload --port 5555
endif
	uvicorn main:app --host 0.0.0.0 --reload --port "$(p)"
