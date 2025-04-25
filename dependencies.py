import psycopg2
from dotenv import load_dotenv
import os
from contextlib import contextmanager

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def instance_cursor():
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed")

def create_table():
    with instance_cursor() as cursor:
        query = '''
        CREATE TABLE IF NOT EXISTS registers (
            name VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            mail VARCHAR(255),
            password VARCHAR(255)
        )
        '''
        cursor.execute(query)
        print('Table created')


def add_username(name, username, mail, password):
    with instance_cursor() as cursor:
        query = '''
            INSERT INTO registers (name, username, mail, password)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (name, username, mail, password))

def get_all_usernames():
    with instance_cursor() as cursor:
        query = '''
            SELECT * 
            FROM registers
        '''
        cursor.execute(query)
        result = cursor.fetchall()
        return result


def get_username_by_username(username):
    with instance_cursor() as cursor:
        query = '''
        SELECT name, username, mail, password
        FROM registers
        WHERE username = %s
        '''
        cursor.execute(query, (username,))
        result = cursor.fetchall()
        return result

def update_password(username, new_password):
    with instance_cursor() as cursor:
        query = '''
        UPDATE registers
        SET password = %s
        WHERE username = %s
        '''
        cursor.execute(query, (new_password, username))