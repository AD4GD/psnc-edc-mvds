# User Management Service

## How to run
source .venv/bin/activate
pip install -r requirements.txt

## Generate migration file (requires db connection)
alembic revision --autogenerate -m "<Msg>"

## Delete all data from the DB
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;