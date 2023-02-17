from tests.extensions import *
from flask_testing import TestCase
from app import *
from tests.instance import BaseTestCase
from flask import request, url_for
import re

client = app.test_client()

# Sample form info for testing
form1 = dict(email='ccc', name='bob', subject='question', message='')
form2 = dict(email='', name='bob', subject='question', message='some message')

class TestEnquiryFeature(MockDB, BaseTestCase):

    def test_enquiry_page_loads_valid(self):
        response = client.get('/contact_us')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Contact Us", response.data)
        self.assert_template_used('customer/enquiry_form.html')
    
    def test_enquiry_page_returns_correct_template(self):
        response = client.get('/contact_us')
        self.assert_template_used('customer/enquiry_form.html')

    def test_enquiry_page_has_correct_form(self):
        with client.get('/contact_us'):
            form = ContactForm()
            self.assertIsInstance(form, ContactForm)
        
    def test_enquiry_form_returns_form_errors_if_invalid(self):
        response1 = client.post('/contact_us', data=form1)
        response2 = client.post('/contact_us', data=form2)

        self.assertIn(b'Please enter a valid email address!', response1.data)
        self.assertTrue(re.search('All fields are required.', response2.get_data(as_text=True)))