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
