# Projet Intelligence Artificielle
Instructions afin de faire les migrations:
-Supprimer les dossiers de migrations
-Supprimer (éventuellement) la dbsq_lite
-Utiliser:
1."python manage.py makemigrations game"
2."python manage.py makemigrations AI"
3."python manage.py makemigrations connection"
4."python manage.py migrate --run-syncdb"