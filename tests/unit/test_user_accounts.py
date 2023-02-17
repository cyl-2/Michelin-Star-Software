from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for

client = app.test_client()
form1 = dict(email='cherrylincyl@gmail.com', password='ABC123abc???!',confirm='ABC123abc???!',first_name='Cherry', last_name='Lin')

class TestAccounts(MockDB, BaseTestCase):

    def test_registration_db(self):
        # tests that CRUD operations can be made to the db
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""INSERT INTO customer (customer_id, email, first_name, last_name, password) VALUES
                            (1, 'email2@gmail.com', 'john', 'smith', "password123")"""), False)
            self.assertEqual(utils.db_write("""INSERT INTO customer (email, first_name, last_name, password) VALUES
                            ('email3@gmail.com', 'jsdsafd', 'fdaffafd', "hfgddg")"""), True)

            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=1"""), True)
            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=4"""), True)

            self.assertEqual(utils.db_read("""SELECT customer_id, email, first_name, last_name, password 
                                FROM customer WHERE customer_id=2"""), [2, 'email2@gmail.com', 'mary', 'murphy', 'password789'])