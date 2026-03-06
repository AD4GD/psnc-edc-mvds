# Data Space Hub

## How to run
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8300

## Generate migration file (requires db connection)
alembic revision --autogenerate -m "<Msg>"

## Delete all data from the DB
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;