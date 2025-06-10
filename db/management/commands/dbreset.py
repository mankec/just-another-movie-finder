import psycopg
from django.core.management.base import BaseCommand
from environs import Env

from db.constants import POSTGRES_DEFAULT_DB

env = Env()

class Command(BaseCommand):
    help = "Drop and then create database again. Useful when you want to migrate from a scratch."

    def handle(self, *_args, **_options):
        conninfo = f"dbname={POSTGRES_DEFAULT_DB} user={env.str("POSTGRES_USER")} password={env.str("POSTGRES_PASSWORD")} host={env.str("POSTGRES_HOST")}"

        with psycopg.connect(conninfo, autocommit=True) as conn:
            db_exists = conn.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{env.str("POSTGRES_DB")}'"
            ).fetchone()

            if db_exists:
                conn.execute(f"DROP DATABASE {env.str("POSTGRES_DB")};")
                print(f"Dropped database '{env.str("POSTGRES_DB")}'.")

                conn.execute(f"CREATE DATABASE {env.str("POSTGRES_DB")}")
                print(f"Created database '{env.str("POSTGRES_DB")}'.")
            else:
                print("Database doesn't exist. Run 'dbcreate' to create it.")
