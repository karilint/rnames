# Development Environment

## Install Docker

First, you need to have Docker and Docker Compose installed on your system. 

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Environment variables

Create a `.env` file in the root of the repository and write needed environment variables to it. You can take the [Example .env](./.env.example) and fill in couple of the variables according to the [Environment variable docs](./environment_variables.md).

## Running the environment

To start the environment, you have to run this command in the root the repository. 
```
docker-compose up -d --build
```
Now if you go to [localhost:8000](localhost:8000), you should see the RNames app running. You can also go to [localhost:8001](localhost:8001) to see or modify the created database. If the website doesn't show up, check the logs. Most likely the service just hasn't started yet. 

You can make changes to the django app in real time when the containers are running. The [App](./../app) directory has been binded to the rnames_web container so that all the changes to the host machine's [App](./../app) directory are also made in the container. 

To see logs you can run this command. You can also specify a container if you only want to see specific logs `docker-compose logs -f <container>`. 
```
docker-compose logs -f
```
NOTE: The logs may show a failure to run tests the first time the containers are built in a new environment. This is normal; see **Running tests** (below) on how to resolve this issue.

If you want to shutdown the containers, you can run this command. 
```
docker-compose down
```
In the case of wanting to also remove the volumes (meaning that the database will be reset), you can run `docker-compose down -v`.

### Other useful commands

You can execute commands inside the container by running:
```
docker-compose exec <container> <command>
```
For example, if you need to make migrations inside django, you can run `docker-compose exec web python manage.py makemigrations`. Then to migrate the database you can run `docker-compose exec web python manage.py migrate`. These commands should usually been run when the developer has made changes to the models or created a new app inside django. See more in [Django docs](https://docs.djangoproject.com/en/3.2/).

Please note that currently the django application makes migrations and migrates the database every time the django container is started. If this proves to be cumbersome the lines can be commented out in [entrypoint.sh](./../app/scripts/entrypoint.sh).

## Running tests
Tests are run automatically when the containers are built. Note, however, that they may fail unless proper privileges for Django have been set; see the subsection on Setting privileges (below). Once the privileges are set, tests can also be run manually with the command
```
docker exec rnames_web python3 manage.py test 
```

### Setting privileges

Django will not run any tests unless it can construct a test database. The privileges it requires for doing this must currently be set manually.

Once the containers are running, open the database in MySQL with root privileges:
```
docker exec -it rnames_db mysql -uroot -p  
```
MySQL will ask for a password; the one required is specified by the variable DB_ROOT_PASSWORD in the .env file (_rootpassword_ in the [Example .env](./.env.example)).

Once in MySQL, a list of users can be obtained by entering the following command:
```
SELECT User, Host, authentication_string FROM mysql.user; 
```
By default, Django should have its username listed as _django_rnames_ and its host as _%_. (If this is not the case, then substitute these values with the listed username and host, respectively, in the following command below.)

Grant all privileges to Django:
```
GRANT ALL PRIVILEGES ON *.* TO 'django_rnames'@'%';
```
Finally, run:
```
FLUSH PRIVILEGES;
```
The tests should now work. Exit MySQL with the command `QUIT`.

## User groups and permissions

RNames does not require user registration/login for viewing. However, adding, editing or exporting data is restricted to three _user groups_:
- _registered users_ can export certain data as .csv files.
- _data contributors_ can add data to the database as well as edit or delete their own contributions.
- _data admins_ can freely add, edit or delete data in the database.

These restrictions are enforced by the code, but setting up the user groups and adding new users in the database must currently be done manually.
Once the containers are running, open Django Admin in a web browser: http://localhost:8000/admin/. The site will ask you to log in; by default the username is _admin_ and the password is _password_.
To add a group, click on _Add_ under _Authentication and Authorization – Groups_.
- Enter a name for the group. The name should be either _registered_, _data_contributor_ or _data_admin_, depending on which group is currently being created.
- Grant permissions to the group. In the current implementation, groups _data_contributor_ and _data_admin_ have been granted all permissions (with more specific restrictions being handled by the code). This can be done simply by clicking on _Choose all_ under the _Permissions_ list. Group _registered_ has been granted all viewing permissions; type `view` into the _Filter_ field and then click on _Choose all_.
- Save the group by clicking _Save_.

To add a user, click on _Add_ under _Authentication and Authorization – Users_.
- Enter a username, password and e-mail address for the user. Note that these must be unique for each user. Other fields are optional.
- Select a group for the user from the group list and add it by clicking on the right-pointing arrow button between the lists. It is technically possible to add more than one group, but there is no need for it in the current implementation; e.g. the group _registered_ does not have any permissions that _data_contributor_ or _data_admin_ do not have.
- Save the user by clicking _Save_.

When signing in as a new user in RNames for the first time, the application is supposed to send a verification link to the user’s e-mail address (and will claim to have done so), but due to how the e-mail backend is currently configured, this does not actually happen.
One way to verify a user’s e-mail address is the following:
1. Attempt to sign in as the new user in RNames.
2. Navigate to http://localhost:8001/
3. Open the database table _account_emailaddress_ under _django_rnames_.
4. Click _Edit_ on the e-mail address to be verified, and enter `1` into the columns _verified_ and _primary_.
