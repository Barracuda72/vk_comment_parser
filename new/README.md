# Setup

## RabbitMQ

- Install rabbitmq-server and python3-pika
- Enable rabbitmq-server and start it with systemctl
- Change default password with "rabbitmqctl change_password guest newpassword"
- Edit config.py and set new password and queue name

## Postgres

- Install postgresql postgresql-contrib python3-psycopg2
- Enable postgresql and start it with systemctl
- Create new user with "createuser --interactive" as 'postgres' user
- Change user password with "\password username" comand from psql CLI
- Create new database with "createdb dbname" as 'postgres' user
- Grant user access to the created database with "GRANT ALL PRIVILEGES ON DATABASE database_name TO username;" from psql CLI
- Edit config.py and set database name, user and password
