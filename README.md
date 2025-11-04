# JAMF - Just Another Movie Finder

## Guide for setting up project on Ubuntu

Requirements:
- pipenv
- direnv
- PostgreSQL


### pipenv

```
pip install --user pipenv
```
More info [here](https://pipenv.pypa.io/en/latest/installation.html).

### Install Python packages

```
pipenv install
```

### Install Node packages

```
npm i
```

### direnv

```
sudo apt install direnv
```
Add to `~/.bashrc`.
```
eval "$(direnv hook bash)"
```
You can read more about setup [here](https://direnv.net/docs/hook.html).

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

## Ngrok

Perhaps you want to test some feature on a phone? Download [ngrok](https://ngrok.com/download/linux) and then run `ngrok http 8000`. In `base.html` use built assets instead of ones served from `localhost:5173`. In order to do this comment out line that looks like this

```
<link rel="stylesheet" href="http://localhost:5173/core/static/src/styles/main.css">
```

And use this one instead

```
<link rel="stylesheet" href="{% vite_asset_path "core/static/src/styles/main.css" %}">
```

Don't forget to do the same for JS.

You will need to run `npx vite build` in order for changes to reflect in your web browser. I was too lazy of finding a better solution since it's not front-end heavy app but PR for this is greatly appreciated!

## Running tests

```
DJANGO_ENV=test python manage.py test
```
More about Django testing [here](https://docs.djangoproject.com/en/5.2/topics/testing/).
