
Developer Login are:

login = developer

password = developer


Player Login are:

login = player

password = player


To reset all migrations:
```
cd /game_application/game_project
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
sudo rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
```
