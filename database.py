#!/usr/bin/python

import psycopg2
import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE registers (
            user_id VARCHAR(255) NOT NULL,
            movie_id VARCHAR(255) NOT NULL,
            movie_name VARCHAR(255),
            PRIMARY KEY (user_id , movie_id)
        )
        """)
    conn = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_register(user_id, movie_id, movie_name):
    sql = """INSERT INTO registers(user_id)
             VALUES(%s, %s, %s) RETURNING movie_id;"""
    conn = None
    movie_id = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (user_id, movie_id, movie_name))
        # get the generated id back
        movie_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return movie_id


def get_registers(movie_id):
    conn = None
    result = []
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT user_id, movie_id FROM registers WHERE movie_id = %s" % movie_id)
        print("The number of registers: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            result.append(row)
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result


def get_subscriptions(user_id):
    conn = None
    result = []
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT movie_name FROM registers WHERE user_id = %s" % user_id)
        print("The number of registers: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            result.append(row)
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result
