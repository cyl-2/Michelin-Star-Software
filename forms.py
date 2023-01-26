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
    email = StringField('Email Address', validators=[InputRequired("Email doesn't exist")])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    name = StringField(validators=[InputRequired()])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class ReplyForm(FlaskForm):
    email = StringField("Email Address", [validators.Length(min=6, max=100)])
    subject = StringField(validators=[InputRequired()])
    message = TextAreaField(validators=[InputRequired()], widget=TextArea())
    submit = SubmitField("Send message")

class EmployeeForm(FlaskForm):
    first_name = StringField("First name ", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    email = StringField("Email Address",[validators.Length(min=6, max=100)])
    address = TextAreaField("Address")
    bio = TextAreaField("About Info", widget=TextArea())
    role = StringField("Role: ", default="", validators=[InputRequired()])
    access_level = SelectField("Choose an option", 
                                        choices = [("managerial", "Managerial"),
                                                    ("ordinary staff", "Ordinary staff")], validators=[InputRequired()])
    submit = SubmitField("Create")

class NewPasswordForm(FlaskForm):
    new_password = PasswordField("New Password", validators=[InputRequired()])
    password2 = PasswordField("Confirm new password", validators=[InputRequired("Password doesn't match"), EqualTo("new_password")])
    submit = SubmitField("Change password")

class ResetPasswordForm(FlaskForm):
    role = RadioField("Are you a...", 
    choices = [("customer", "Customer"),
                ("staff", "Staff member")], validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired("Please fill in an email address")])
    submit = SubmitField("Change password")

class CodeForm(FlaskForm):
    code = StringField('Enter the 5 digit code here', validators=[InputRequired("Wrong code")])
    submit = SubmitField("Submit")

class RosterRequestForm(FlaskForm):
    message = TextAreaField("Message", widget=TextArea(), validators=[InputRequired("Enter a message")])
    submit = SubmitField("Submit")