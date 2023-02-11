from wtforms import SubmitField, StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField, DecimalField, RadioField, validators
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange, Email
from wtforms.widgets import TextArea

class TableForm(FlaskForm):
    table_number = IntegerField( validators=[InputRequired(), NumberRange(1,100)])
    seats = IntegerField(validators=[InputRequired(), NumberRange(1,25)])
    x = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    y = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    submit = SubmitField("Create Table")
    
    
class AddToRosterForm(FlaskForm):
    staff_id = IntegerField( validators=[InputRequired(), NumberRange(1,100)])
    day = SelectField(validators=[InputRequired()], choices=[
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')])
    time = StringField(validators=[InputRequired()])
    submit = SubmitField("Add to Roster")
    
class RosterRequirementsForm(FlaskForm):
    day = SelectField(validators=[InputRequired()], choices=[
        ('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
        ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')])
    opening_time = IntegerField( validators=[ NumberRange(0,24)])
    closing_time = IntegerField( validators=[ NumberRange(0,24)])
    min_workers = IntegerField( validators=[ NumberRange(0,24)])
    
    unavailable = StringField()
    submit = SubmitField("Change Requirements")


class RegistrationForm(FlaskForm):
    email = StringField("Email Address", [InputRequired(), validators.Length(min=6, max=100), Email(message="Please enter a valid email address!")])
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
    role = StringField("Role: ", validators=[InputRequired()])
    access_level = SelectField("Choose an option", 
                                        choices = [("managerial", "Managerial"),
                                                    ("ordinary staff", "Ordinary staff")], validators=[InputRequired()])
    submit = SubmitField("Create")

class ProfileForm(FlaskForm):
    email = StringField("Email Address", validators=[InputRequired()])
    first_name = StringField("First name ", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    address = StringField("Address")
    bio = TextAreaField("About Info", widget=TextArea())
    submit = SubmitField("Update")

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

class RejectRosterRequestForm(FlaskForm):
    response = TextAreaField("Reason for rejection", widget=TextArea(), validators=[InputRequired()])
    submit = SubmitField("Confirm")

class submitModifications(FlaskForm):
    submit = SubmitField('Enter')