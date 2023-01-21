from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField, validators
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=5, max=25)])
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired("Username doesn't exist")])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm password", validators=[InputRequired("Password doesn't match"), EqualTo("password")])
    submit = SubmitField("Login")