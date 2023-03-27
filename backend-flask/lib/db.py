import os
import re
import sys
import pathlib
from psycopg_pool import ConnectionPool
from flask import current_app as app


class Db():
    """
    missing class docstring
    """

    def __init__(self):
        self.init_pool()

    def init_pool(self):
        connection_url = os.getenv("CONNECTION_URL")
        self.pool = ConnectionPool(connection_url)

    def print_sql(self, title, sql):
        cyan = '\033[96m'
        no_color = '\033[0m'
        print(f'{cyan} SQL STATEMENT--{title}-------{no_color}')
        print(sql + '\n')

    def load_template(self, *args):
        """
        loads sql statement into a string
        """
        green = '\033[92m'
        no_color = '\033[0m'
        print(f'{green} PATH {no_color}')

        app_path = pathlib.Path('.')
        template_path = app_path.joinpath(
            app.root_path, 'db', 'sql', *args).with_suffix('.sql')
        template_content = template_path.read_text()
        return template_content

    def query_commit(self, sql, params):
        # change to CloudWatch logging later on
        self.print_sql('query_commit', sql)
        print(f"THIS IS HANDLE: {params}")

        pattern = r"\bRETURNING\b"
        is_returning_id = re.search(pattern, sql)

        try:
            with self.pool.connection() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                if is_returning_id:
                    returning_id = cur.fetchone()[0]
                conn.commit()
                if is_returning_id:
                    return returning_id
        except Exception as error:
            self.print_sql_err(error)
            # conn.rollback()
        finally:
            print('query_commit finished')

    def query_object_json(self, sql, params):
        """
        when we want to return a json object
        """
        self.print_sql('query_object_json', sql)
        print('PARAMS: ')
        print(params)

        wrapped_sql = self.query_wrap_object(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql, params)
                json = cur.fetchone()

                if json is None:
                    return "{}"
                else:
                    return json[0]

    def query_array_json(self, sql, params):
        """
        when we want to return and array of json objects
        """
        self.print_sql('query_array_json', sql)
        wrapped_sql = self.query_wrap_array(sql)
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(wrapped_sql, params)
                # this will return a tuple
                # the first field being the data
                json = cur.fetchone()
                return json[0]

    def print_sql_err(self, err):
        """
        we copied this function from: Python Error Handling with the Psycopg2 PostgreSQL Adapter 645
        https://kb.objectrocket.com/postgresql/python-error-handling-with-the-psycopg2-postgresql-adapter-645
        """
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get the line number when exception occured
        line_num = traceback.tb_lineno

        # print the connect() error
        print("\npsycopg2 ERROR:", err, "on line number:", line_num)
        print("psycopg2 traceback:", traceback, "-- type:", err_type)

        # psycopg2 extensions.Diagnostics object attribute
        # print ("\nextensions.Diagnostics:", err.diag)

        # print the pgcode and pgerror exceptions
        print("pgerror:", err.pgerror)
        print("pgcode:", err.pgcode, "\n")

    def query_wrap_object(self, template):
        """
        wraps query result into a JSON object
        """
        sql = f"""
            (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
            {template}
            ) object_row);
            """
        return sql

    def query_wrap_array(self, template):
        """
        wraps query reult in array of JSON objects
        """
        sql = f"""
            (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
            {template}
            ) array_row);
            """
        return sql


db = Db()
