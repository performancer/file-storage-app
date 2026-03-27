# File Storage Application

This is an application for storing files. Users that are assigned to organizations may share files and users from other organizations may download them. Downloads are recorded and fetchable by user and file. Also organization download counts are available.

## How to run and test the application

Build and run the docker compose:

```docker compose up```

Once up, the API will be available at ```127.0.0.1:8000```.

Then migrate:

```docker compose run web python manage.py migrate```

Create a user (or multiple) to log in

```docker compose run web python manage.py createsuperuser```

Create `organization`s in the admin backoffice in ```127.0.0.1:8000/admin/```

Connect the organizations to users with `organization user`s.

Once you are logged in with a user account that is in an organization, you may upload, fetch and download files and other data.

You may always run the test suite with:
```docker compose run web python manage.py test```

## Endpoints to Explore

To upload a file:
POST ```/files/```

To fetch all uploaded files:
GET ```/files/```

To fetch details of a specific file:
GET ```/files/<file-id>/```

To fetch list of all organizations:
GET ```/organizations/```

To download a file:
GET ```/download/<file_id>/```

To fetch all downloads per user:
GET ```/downloads/user/<user-id>```

To fetch all downloads per file:
GET ```/downloads/file/<file_id>```

Django Admin Backoffice:
```/admin/*```

Django REST Framework urls:
```/api-auth/*```


## Cheat Sheet for Development

### Add a new app

```docker compose run web python manage.py startapp <app>```

### Migrations
```docker compose run web python manage.py makemigrations```

```docker compose run web python manage.py migrate```

### Create a superuser

```docker compose run web python manage.py createsuperuser```

### Run the tests

```docker compose run web python manage.py test```