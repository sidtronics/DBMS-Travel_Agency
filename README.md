# DBMS-Travel_Agency

## Installation
```bash
git clone https://github.com/sidtronics/DBMS-Travel_Agency.git
cd DBMS-Travel_Agency

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## MariaDB

### Installation:
MariaDB Installation and Configuration: [ArchWiki](https://wiki.archlinux.org/title/MariaDB)

### Configure as follows:
user: root
password: root

### Start MariaDB
```bash
sudo systemctl start mariadb
```

## Start Server
```bash
python app.py
```

Note: will automatically generate database and schema.

## Stop
```bash
sudo systemctl stop mariadb
deactivate
```
