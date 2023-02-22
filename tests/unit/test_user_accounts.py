from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for

client = app.test_client()
form1 = dict(email='cherrylincyl@gmail.com', password='ABC123abc???!',confirm='ABC123abc???!',first_name='Cherry', last_name='Lin')

class TestAccounts(MockDB, BaseTestCase):
    # tests that CRUD operations can be made to the db
    def test_customer_registration_db_create_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""INSERT INTO customer (email, first_name, last_name, password) VALUES
                            ('email3@gmail.com', 'jsdsafd', 'fdaffafd', "hfgddg")"""), True)
    
    def test_customer_registration_create_operation_returns_false_if_a_customer_id_is_already_taken(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""INSERT INTO customer (customer_id, email, first_name, last_name, password) VALUES
                            (1, 'email2@gmail.com', 'john', 'smith', "password123")"""), False)

    def test_customer_registration_db_read_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_read("""SELECT customer_id, email, first_name, last_name, password 
                                FROM customer WHERE customer_id=2"""), [2, 'email2@gmail.com', 'mary', 'murphy', 'password789'])

    def test_customer_registration_db_update_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""UPDATE customer SET first_name='Megan' WHERE customer_id=2"""), True)
            self.assertEqual(utils.db_read("""SELECT first_name FROM customer WHERE customer_id=2"""), ["Megan"])

    def test_customer_registration_db_delete_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=1"""), True)
            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=4"""), True)

    def test_staff_registration_db_create_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""INSERT INTO staff (email, first_name, last_name, password, access_level, role) VALUES
                            ('djacjs@gmail.com', 'betty', 'smith', "password123", 'managerial', 'Manager')"""), True)
            self.assertEqual(utils.db_write("""INSERT INTO staff (email, first_name, last_name, password, access_level, role) VALUES
                            ('ofieh@gmail.com', 'harry', 'styles', "hfgfgfddg", 'ordinary staff', 'Waiter')"""), True)
    
    def test_staff_registration_db_read_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_read("""SELECT staff_id, first_name
                                FROM staff WHERE staff_id=1"""), [1, 'betty'])

    def test_staff_registration_db_update_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""UPDATE staff SET first_name='Spongebob' WHERE staff_id=1"""), True)
            self.assertEqual(utils.db_read("""SELECT first_name FROM staff WHERE staff_id=1"""), ["Spongebob"])
            
    def test_staff_registration_db_delete_operation(self):
        with self.mock_db_config:
            self.assertEqual(utils.db_write("""DELETE FROM staff WHERE staff_id=2"""), True)                    