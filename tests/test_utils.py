from extensions import MockDB, patch, utils, responses, TestCase, Flask
from forms import RegistrationForm

class TestUtils(MockDB):

    def test_registration(self):
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "MY_SECRET_KEY"

        with app.test_request_context('/'):
            form = RegistrationForm()
        self.assertIsInstance(form, RegistrationForm)

        with self.mock_db_config:

            self.assertEqual(utils.db_write("""INSERT INTO customer (customer_id, email, first_name, last_name, password) VALUES
                            (1, 'email2@gmail.com', 'john', 'smith', "password123")"""), False)
            self.assertEqual(utils.db_write("""INSERT INTO customer (email, first_name, last_name, password) VALUES
                            ('email3@gmail.com', 'jsdsafd', 'fdaffafd', "hfgddg")"""), True)

            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=1"""), True)
            self.assertEqual(utils.db_write("""DELETE FROM customer WHERE customer_id=4"""), True)

            self.assertEqual(utils.db_read("""SELECT customer_id, email, first_name, last_name, password 
                                FROM customer WHERE customer_id=2"""), [2, 'email2@gmail.com', 'mary', 'murphy', 'password789'])
