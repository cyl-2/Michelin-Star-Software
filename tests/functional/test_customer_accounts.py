from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for

client = app.test_client()

# User details for testing
Person1 = dict(email='ccc', password='blah',confirm='blah',first_name='mary', last_name='smith')
Person2 = dict(email='cccccc@gmail.com', password='',confirm='',first_name='mary',last_name='smith')
Person3 = dict(email='', password='')

class TestCustomerFeatures(MockDB, BaseTestCase):

    def test_registration_page_loads_successfully(self):
        response = client.get('/registration')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration", response.data)
    
    def test_registration_route_returns_correct_template(self):
        response = client.get('/registration')
        self.assert_template_used('customer/registration.html')

    def test_registration_page_has_correct_form(self):
        with client.get('/registration'):
            form = RegistrationForm()
            self.assertIsInstance(form, RegistrationForm)
        
    def test_registration_form_returns_form_errors_if_invalid_parameters(self):
        response1 = client.post('/registration', data=Person1, follow_redirects=True)
        response2 = client.post('/registration', data=Person2, follow_redirects=True)

        self.assertIn(b'Please enter a valid email address!', response1.data)
        self.assertIn(b'This field is required', response2.data)
    
    def test_login_page_loads_successfully(self):
        response = client.get('/customer_login')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Customer Login", response.data)
    
    def test_login_page_returns_correct_template(self):
        response = client.get('/customer_login')
        self.assert_template_used('customer/customer_login.html')

    def test_login_page_has_form(self):
        with client.get('/customer_login'):
            form = LoginForm()
            self.assertIsInstance(form, LoginForm)
    
    def test_login_form_returns_form_errors_if_invalid(self):
        response = client.post('/customer_login', data=Person3, follow_redirects=True)
        self.assertIn(b'This field is required', response.data)
    
    def test_profile_page_returns_error_if_not_logged_in(self):
        response = client.get('/customer_profile')
        self.assertEqual(response.status_code, 404)