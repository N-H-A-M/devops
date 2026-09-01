# devops
dev branch.
source .venv/bin/activate #activate .venv 
requirements:
python3.14


needs to have a .env at root of the folder 
DATABASE_URL- database url in container
DATABASE_URL_EX - outside container
ALLOWED_ORIGINS= port and url of the front end
DB_USER= db user
DB_PASSWORD= passwrod
DB_NAME= name of DB
PROJECT_ROOT=.

needs to have a .env.secret in deploy/k8s/base