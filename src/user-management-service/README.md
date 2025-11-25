# User Management Service

## How to run
source .venv/bin/activate
pip install -r requirements.txt

## Generate migration file (requires db connection)
alembic revision --autogenerate -m "<Msg>"