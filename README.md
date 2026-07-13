# devops
dev branch.
source .venv/bin/activate #activate .venv 
requirements:
python3.14


scripts:
make sure the file is executable
chmod +x startup.sh
./stratup.sh
wipe the database: 
sudo -u postgres psql -c "DROP DATABASE cards_db;"