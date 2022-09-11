import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


def load_credentials():
    load_dotenv()  # take environment variables from .env.

    # Database settings
    username = os.environ.get('POSTGRES_USERNAME')
    password = os.environ.get('POSTGRES_PASSWORD')
    hostname = os.environ.get('POSTGRES_HOSTNAME')
    port = os.environ.get('POSTGRES_PORT')
    database = os.environ.get('POSTGRES_DATABASE')

    return {'username': username,
            'password': password,
            'hostname': hostname,
            'port': port,
            'database': database}


def get_table(table, verbose=True):
    if verbose:
        print(f'Importing {table} data from postgres db')

    env = load_credentials()
    conn = psycopg2.connect(host=env['hostname'],
                            user=env['username'],
                            password=env['password'],
                            dbname=env['database'],
                            port=env['port'])
    df = pd.read_sql_table(table, conn)
    conn.close()
    return df


def export_to_table(dataframe, table, verbose=True):
    if verbose:
        print(f'Exporting {table} data to postgres db')

    env = load_credentials()
    conn = psycopg2.connect(host=env['hostname'],
                            user=env['username'],
                            password=env['password'],
                            dbname=env['database'],
                            port=env['port'])
    dataframe.to_sql(table, con=conn, if_exists='replace', index=False)
    conn.close()

    if verbose:
        print(f'{table} exported')
