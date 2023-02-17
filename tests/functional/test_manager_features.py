from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for
import re

client = app.test_client()

# Sample form info for testing
form1 = dict(first_name='', last_name='', email='', role='', access_level='')

class TestManagerFeatures(MockDB, BaseTestCase):
    def test_add_new_staff_page_loads(self):
        response = client.get('/add_new_employee')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"New Employee Registration", response.data)
        self.assert_template_used('manager/add_new_staff.html')

    def test_add_new_staff_page_has_form(self):
        with client.get('/add_new_employee'):
            form = EmployeeForm()
            self.assertIsInstance(form, EmployeeForm)

    def test_add_new_staff_form_returns_form_errors_if_invalid(self):
        response = client.post('/add_new_employee', data=form1)
        self.assertIn(b'This field is required', response.data)
        password = get_random_password()
        self.assertNotEqual("132123212", password)