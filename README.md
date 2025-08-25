# JAMF - Just Another Movie Finder

## Guide for setting up project on Ubuntu

Requirements:
- pipenv
- direnv
- PostgreSQL


### pipenv

More info [here](https://pipenv.pypa.io/en/latest/installation.html).
```
pip install --user pipenv
```

### Install Python packages

```
pipenv install
```

### Install Node packages

```
npm i
```

### direnv

You can read about setup [here](https://direnv.net/docs/hook.html).
```
sudo apt install direnv
```
Add to `~/.bashrc`.
```
eval "$(direnv hook bash)"
```

### PostgreSQL

```
sudo apt install postgresql postgresql-contrib
```

Open terminal.
```
sudo -i -u postgres psql
```
Create sudo role. Don't forget to put semicolon at the end.
```
CREATE ROLE myuser WITH LOGIN SUPERUSER PASSWORD 'password';
```
Quit terminal with `ctrl + d` or type `\q` in terminal.
Create new database. Name it as you wish.
```
createdb jamf_dev
```

Get connection info about your database.
```
psql jamf_dev
\conninfo
```
Create `.envrc`
```
direnv allow .
cp .envrc.example .envrc
```
Update values in `.envrc` with values from `/conninfo` e.g. `POSTGRES_DB` should be `jamf_dev` instead of `dbname`.

## Run migrations

```
python manage.py migrate
```

## Seed database

```
python manage.py dbseed
```

## Starting a server

You will need to run two servers. Second one is for JavaScript and CSS.
```
python manage.py runserver
npx vite
```
