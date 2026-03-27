## Cheat Sheet

### Add a new app

```docker compose run web python manage.py startapp <app>```

### Migrations
```docker compose run web python manage.py makemigrations```

```docker compose run web python manage.py migrate```

### Create a superuser

```docker compose run web python manage.py createsuperuser```

### Run the tests

```docker compose run web python manage.py test```