import psycopg2
from psycopg2 import sql

HOST = "127.0.0.1"
USER = "postgres"
PASSWORD = "2108"
DB_NAME = "weather"
PORT = "5432"


def create_data_base():
    connection = None
    try:
        connection = psycopg2.connect(dbname="postgres", user=USER, password=PASSWORD, host=HOST, port=PORT)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}").format(sql.Literal(DB_NAME))
            )
            exists = cursor.fetchone()

            if not exists:
                query = f"CREATE DATABASE {DB_NAME};"
                cursor.execute(query)
                print(f"База данных {DB_NAME} создана.")
            else:
                print(f"База данных {DB_NAME} уже существует.")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL 1", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def create_table(table_name):
    connection = None
    try:
        connection = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        connection.autocommit = True

        with connection.cursor() as cursor:
            query = f"CREATE TABLE {table_name} (station TEXT, date DATE, temperature REAL, PRIMARY KEY (station, date));"
            cursor.execute(query)

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL 2", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")


def convert_to_date(month_year):
    month, year = month_year.split(".")
    return f"{year}-{month}-01"


def insert_into_db(db_name, station_name, data):
    connection = None
    try:
        connection = psycopg2.connect(dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT)
        connection.autocommit = True

        with connection.cursor() as cursor:
            for ind in range(data.shape[0]):
                row = data.iloc[ind].values
                query = f"INSERT INTO {db_name} (station, date, temperature) VALUES (%s, %s, %s);"
                converted_data = (station_name, convert_to_date(row[0]), float(row[1]))
                cursor.execute(query, converted_data)
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if connection:
            connection.close()
            print("[INFO] PostgreSQL connection closed")
