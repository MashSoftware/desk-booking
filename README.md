# Flask Bootstrap All-in-One Template

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N33KKEF)

## Prerequisites

### Required

- Python 3.7.x or higher
- PostgreSQL 11.x or higher

### Optional

- Redis 4.0.x or higher (for rate limiting, otherwise in-memory storage is used)

## Getting started

### Create local Postgres database

```shell
sudo service postgresql start
sudo -su postgres
psql
create user mash with password 'mash';
createdb thing;
grant all privileges on database thing to mash;
```

### Create venv and install requirements

```shell
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt ; pip3 install -r requirements_dev.txt
```

### Run database migrations

```shell
flask db upgrade
```

### Run app

```shell
flask run
```

## Testing

Run the test suite

```shell
python -m pytest --cov=app --cov-report=term-missing --cov-branch
```