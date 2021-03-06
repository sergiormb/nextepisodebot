#!/usr/bin/python

import psycopg2
import config


def create_tables():
    """ create tables in the PostgreSQL database"""
    command = """
        CREATE TABLE subscriptions (
            user_id VARCHAR(255) NOT NULL,
            serie_id VARCHAR(255) NOT NULL,
            chat_id INTEGER NOT NULL,
            serie_name VARCHAR(255),
            PRIMARY KEY (user_id , serie_id)
        )
        """
    conn = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        # cur.execute("DROP TABLE subscriptions;")
        # cur.close()
        # conn.commit()
        # conn = psycopg2.connect(**params)
        # cur = conn.cursor()
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


def insert_register(user_id, serie_id, chat_id, serie_name):
    sql = """INSERT INTO subscriptions(user_id, serie_id, chat_id, serie_name)
             VALUES(%s, %s, %s, %s) RETURNING serie_id;"""
    conn = None
    chat_id = int(chat_id)
    response = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (user_id, serie_id, chat_id, serie_name))
        # get the generated id back
        response = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return response


def remove_register(user_id, serie_id):
    sql = """DELETE FROM subscriptions
             WHERE user_id = '%s' AND serie_id = '%s';"""
    conn = None
    response = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (user_id, serie_id))
        # get the generated id back
        response = True
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return response


def get_registers(serie_id):
    conn = None
    result = []
    serie_id = int(serie_id)
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM subscriptions WHERE serie_id = '%s'" % serie_id)
        row = cur.fetchone()

        while row is not None:
            result.append(row[0])
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result


def search(user_id, serie_id):
    conn = None
    result = None
    try:
        # read the connection parameters
        params = config.params
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT serie_name FROM subscriptions WHERE user_id = '%s' AND serie_id = '%s'" % (user_id, serie_id))
        row = cur.fetchone()

        result = row

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
        cur.execute("SELECT serie_name FROM subscriptions WHERE user_id = '%s'" % user_id)
        row = cur.fetchone()

        while row is not None:
            result.append(row[0])
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result
