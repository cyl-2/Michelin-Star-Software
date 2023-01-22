from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField, validators
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange
from wtforms.widgets import TextArea

class RegistrationForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired("Email doesn't exist")])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm password", validators=[InputRequired("Password doesn't match"), EqualTo("password")])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    email = StringField(validators=[InputRequired()])
    name = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class ReplyForm(FlaskForm):
    email = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class EmployeeForm(FlaskForm):
    first_name = StringField("First name: ", default="", validators=[InputRequired()])
    last_name = StringField("Last name: ", default="", validators=[InputRequired()])
    email = StringField("Email: ", default="", validators=[InputRequired()])
    role = StringField("Role: ", default="", validators=[InputRequired()])
    submit = SubmitField("Create")