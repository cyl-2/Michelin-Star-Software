from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for
import re

client = app.test_client()

# Sample form info for testing
form1 = dict(email='', password='')
form2 = dict(message='')

class TestStaffFeatures(MockDB, BaseTestCase):
    def test_staff_login_page_loads_successfully(self):
        response = client.get('/staff_login')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)
    
    def test_staff_login_page_returns_correct_template(self):
        response = client.get('/staff_login')
        self.assert_template_used('staff/staff_login.html')

    def test_staff_login_page_has_correct_form(self):
        with client.get('/staff_login'):
            form = LoginForm()
            self.assertIsInstance(form, LoginForm)
        
    def test_staff_login_form_returns_form_errors_if_invalid(self):
        response = client.post('/staff_login', data=form1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required', response.data)

    def test_staff_choose_table_page_loads_successfully(self):
        response = client.get('/choose_table')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Choose A Table", response.data)
        self.assert_template_used('staff/choose_table.html')

    def test_move_tables_page_loads_successfully(self):
        response = client.get('/move_tables')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Change Table Positions", response.data)
        self.assert_template_used('staff/move_tables.html')
    
    def test_roster_request_page_loads_successfully(self):
        response = client.get('/roster_request')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Roster Request", response.data)
        self.assert_template_used('staff/roster_request.html')
    
    def test_roster_request_form_exists(self):
        with client.get('/roster_request'):
            form = RosterRequestForm()
            self.assertIsInstance(form, RosterRequestForm)
        
    def test_roster_request_form_returns_errors_if_invalid(self):
        response = client.post('/roster_request', data=form2)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Enter a message', response.data)
    
    '''def test_take_order_page_returns_success(self):
        response = client.get('/1/take_order')

        #self.assertEqual(response.status_code, 200)
        #self.assertIn(b"Order", response.data)
        self.assert_template_used('staff/take_order.html')'''