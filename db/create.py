import sqlite3
from sqlite3 import Error

PATH = r".\db\example.db"

# flake8: noqa


def create_connection():
    """create a database connection to a database that resides
    in the memory
    """
    conn = None
    try:
        conn = sqlite3.connect(PATH)
    except Error as e:
        print(e)
    finally:
        return conn


def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    # trailing commas will throw a syntax error !?
    sql_create_projects_table = """CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL
                                    );"""

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    project_id integer NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""

    # create a database connection
    conn = create_connection()
    # create tables
    if conn is not None:
        # create projects table
        print("projects")
        create_table(conn, sql_create_projects_table)

        print("tasks")
        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
