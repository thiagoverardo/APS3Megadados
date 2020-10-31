# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import json
import uuid

from functools import lru_cache

import mysql.connector as conn

from fastapi import Depends

from utils.utils import get_config_filename, get_app_secrets_filename

from .models import Task
from .models import User


class DBSession:
    def __init__(self, connection: conn.MySQLConnection):
        self.connection = connection

    def read_tasks(self, completed: bool = None):
        query = 'SELECT BIN_TO_UUID(uuid), description, completed FROM tasks'
        if completed is not None:
            query += ' WHERE completed = '
            if completed:
                query += 'True'
            else:
                query += 'False'

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            db_results = cursor.fetchall()

        return {
            uuid_: Task(
                description=field_description,
                completed=bool(field_completed),
            )
            for uuid_, field_description, field_completed in db_results
        }

    def create_task(self, item: Task):
        uuid_ = uuid.uuid4()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO tasks VALUES (UUID_TO_BIN(%s), %s, %s)',
                (str(uuid_), item.description, item.completed),
            )
        self.connection.commit()

        return uuid_

    def read_task(self, uuid_: uuid.UUID):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT description, completed
                FROM tasks
                WHERE uuid = UUID_TO_BIN(%s)
                ''',
                (str(uuid_), ),
            )
            result = cursor.fetchone()

        return Task(description=result[0], completed=bool(result[1]))

    def replace_task(self, uuid_, item):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE tasks SET description=%s, completed=%s
                WHERE uuid=UUID_TO_BIN(%s)
                ''',
                (item.description, item.completed, str(uuid_)),
            )
        self.connection.commit()

    def remove_task(self, uuid_):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM tasks WHERE uuid=UUID_TO_BIN(%s)',
                (str(uuid_), ),
            )
        self.connection.commit()

    def remove_all_tasks(self):
        with self.connection.cursor() as cursor:
            cursor.execute('DELETE FROM tasks')
        self.connection.commit()

    def __task_exists(self, uuid_: uuid.UUID):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT EXISTS(
                    SELECT 1 FROM tasks WHERE uuid=UUID_TO_BIN(%s)
                )
                ''',
                (str(uuid_), ),
            )
            results = cursor.fetchone()
            found = bool(results[0])

        return found

    # Users

    def read_user(self):
        query = 'SELECT BIN_TO_UUID(uuid), name FROM user'

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            db_results = cursor.fetchall()

        return {
            uuid_: User(
                name=field_name
            )
            for uuid_, field_name in db_results
        }

    def create_user(self, item: User):
        uuid_ = uuid.uuid4()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO user VALUES (UUID_TO_BIN(%s), %s, %s)',
                (str(uuid_), item.name),
            )
        self.connection.commit()

        return uuid_

    def read_user(self, uuid_: uuid.UUID):
        if not self.__user_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT name
                FROM user
                WHERE uuid = UUID_TO_BIN(%s)
                ''',
                (str(uuid_), ),
            )
            result = cursor.fetchone()

        return User(name=result[0])

    def replace_user(self, uuid_, item):
        if not self.__user_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE user SET name=%s
                WHERE uuid=UUID_TO_BIN(%s)
                ''',
                (item.description, item.completed, str(uuid_)),
            )
        self.connection.commit()

    def remove_user(self, uuid_):
        if not self.__user_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM user WHERE uuid=UUID_TO_BIN(%s)',
                (str(uuid_), ),
            )
        self.connection.commit()

    def remove_all_user(self):
        with self.connection.cursor() as cursor:
            cursor.execute('DELETE FROM user')
        self.connection.commit()

    def __user_exists(self, uuid_: uuid.UUID):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT EXISTS(
                    SELECT 1 FROM user WHERE uuid=UUID_TO_BIN(%s)
                )
                ''',
                (str(uuid_), ),
            )
            results = cursor.fetchone()
            found = bool(results[0])

        return found


@lru_cache
def get_credentials(
        config_file_name: str = Depends(get_config_filename),
        secrets_file_name: str = Depends(get_app_secrets_filename),
):
    with open(config_file_name, 'r') as file:
        config = json.load(file)
    with open(secrets_file_name, 'r') as file:
        secrets = json.load(file)
    return {
        'user': secrets['user'],
        'password': secrets['password'],
        'host': config['db_host'],
        'database': config['database'],
    }


def get_db(credentials: dict = Depends(get_credentials)):
    try:
        connection = conn.connect(**credentials)
        yield DBSession(connection)
    finally:
        connection.close()
