# Environment Variables

## Development environment

- DB_HOST should be set as db (database container in docker-compose)
- DB_PORT default is 3306 but if you have other mysql/mariadb services running on your system you might either have to shutdown them or change this. 
- DB_NAME is the name of the database. 
- DB_USER is the name of the database user.
- DB_PASSWORD is the password for the user. 
- DB_ROOT_PASSWORD is the root password for the database. 
- EMAIL_BACKEND defines the email backend django will use. In development, it is usually set as `django.core.mail.backends.console.EmailBackend` so that the emails go to the logs/terminal.
- EMAIL_USER the email django uses. NOT NEEDED when using console emailbackend.
- EMAIL_PASS the password for the email. NOT NEEDED when using console emailbackend.
- ORCID_CLIENT_ID is client id for the orcid authentication. ORCID OAuth will not work without it. 
- ORCID_SECRET is secret for the orcid authentication. ORCID OAuth will not work without it.
- DJANGO_SUPERUSER_USERNAME is the username the django container uses to create a superuser at startup.
- DJANGO_SUPERUSER_PASSWORD is the password the django container uses to create a superuser at startup.
- DJANGO_SUPERUSER_EMAIL is the email the django container uses to create a superuser at startup.
- SITE_NAME is the name for the website. You can set it as RNames.
- SITE_DOMAIN is the domain for the website. In development set is as localhost:8000.
- DJANGO_LOGGING_EMAIL is the email to which detailed debug information is sent when an error occurs with debugging off.

### Other variables (these don't need to be defined)

- SECRET_KEY is the secret key django will use. 
- DEBUG defaults automatically to 1. However, if you want to run the django application without debugging on, you can set this to 0.
- ALLOWED_HOSTS defaults automatically to '*'. But if you want to define certain hosts, they need to seperated by `,`. For example, `127.0.0.1,localhost`.

