from unittest import TestCase
import mysql.connector
from mysql.connector import errorcode
from mock import patch
from . import utils
from . import config

class MockDB(TestCase):
    @classmethod
    def setUpClass(cls):
        cnx = mysql.connector.connect(**config.config)
        cursor = cnx.cursor(dictionary=True)

        # drop table if it already exists
        try:
            cursor.execute("DROP TABLE {}".format(config.T1))
            cursor.close()
            print("DB table dropped")
        except mysql.connector.Error as err:
            print("{}{}".format(MYSQL_DB, err))

        cursor = cnx.cursor(dictionary=True)
        cnx.database = config.MYSQL_DB

        query = """CREATE TABLE customer
                (
                    customer_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    email TEXT NOT NULL,
                    code TEXT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    password TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                );"""
        try:
            cursor.execute(query)
            cnx.commit()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

        insert_data_query = """INSERT INTO customer (email, first_name, last_name, password) VALUES
                            ('email1@gmail.com', 'john', 'smith', "password123"),
                            ('email2@gmail.com', 'mary', 'murphy', "password789")"""
        try:
            cursor.execute(insert_data_query)
            cnx.commit()
        except mysql.connector.Error as err:
            print("Data insertion to table failed \n" + err)
        cursor.close()
        cnx.close()

        testconfig ={
            'host': config.MYSQL_HOST,
            'user': config.MYSQL_USER,
            'password': config.MYSQL_PASSWORD,
            'database': config.MYSQL_DB,
            'auth_plugin': config.AUTH
        }
        cls.mock_db_config = patch.dict(config.config, testconfig)

    @classmethod
    def tearDownClass(cls):
        cnx = mysql.connector.connect(**config.config)
        cursor = cnx.cursor(dictionary=True)

        # drop test database table
        '''try:
            cursor.execute("DROP TABLE {}".format(T1))
            cnx.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print("Table {} does not exists. Dropping db table failed".format(T1))
        cnx.close()'''