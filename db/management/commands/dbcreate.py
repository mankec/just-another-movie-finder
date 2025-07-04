import psycopg
from django.core.management.base import BaseCommand
from environs import Env

from db.constants import POSTGRES_DEFAULT_DB

env = Env()

class Command(BaseCommand):
    help = "Create database using environment variables."

    def handle(self, *_args, **_options):
        conninfo = f"dbname={POSTGRES_DEFAULT_DB} user={env.str("POSTGRES_USER")} password={env.str("POSTGRES_PASSWORD")} host={env.str("POSTGRES_HOST")}"

        with psycopg.connect(conninfo, autocommit=True) as conn:
            db_exists = conn.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{env.str("POSTGRES_DB")}'"
            ).fetchone()

            if not db_exists:
                conn.execute(f"CREATE DATABASE {env.str("POSTGRES_DB")}")
                print(f"Created database '{env.str("POSTGRES_DB")}'.")
            else:
                print("Database already exists.")
