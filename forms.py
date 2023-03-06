from wtforms import SubmitField, StringField, SelectField, PasswordField, DecimalField, TextAreaField, IntegerField, DateField, DecimalRangeField, RadioField, validators, FileField, SelectMultipleField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, EqualTo, NumberRange, Email
from wtforms.widgets import TextArea, CheckboxInput
from flask_wtf.file import FileField, FileAllowed, FileRequired

class TableForm(FlaskForm):
    table_number = IntegerField("Assign Table Number", validators=[InputRequired(), NumberRange(1,100)])
    seats = IntegerField("Number Of Seats", validators=[InputRequired(), NumberRange(1,25)])
    x = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    y = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    submit = SubmitField("Create New Table")
    
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
    submit = SubmitField("Confirm Changes")

class RegistrationForm(FlaskForm):
    email = StringField("Email Address", [InputRequired(), validators.Length(min=6, max=100), Email(message="Please enter a valid email address!")])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password:", validators=[InputRequired(), EqualTo("password")])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    email = StringField("Email Address", [InputRequired(), validators.Length(min=6, max=100), Email(message="Please enter a valid email address!")])
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
    access_level = SelectField("Choose an option for access level", 
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
    password2 = PasswordField("Confirm new password", validators=[InputRequired("Passwords don't match"), EqualTo("new_password")])
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

class AddDishForm(FlaskForm):
    name = StringField('Name: ', validators=[InputRequired()])
    cost = DecimalField('Price', validators=[InputRequired()])
    cookTime= IntegerField('Cook Time (in minutes)', validators=[InputRequired()])
    dishType = SelectField("Category", 
                            choices = [("starter", "Starter"),
                                        ("main course", "Main Course"),
                                        ("dessert", "Dessert"),
                                        ("side", "Side"),
                                        ("drink", "Drink"),
                                        ("special", "Special")], validators=[InputRequired()])
    day = SelectField("Display day for menu item? Menu items are displayed on all days of the week by default", 
                            choices = [(10, "All week"),
                                        (0, "Monday"),
                                        (1, "Tuesday"),
                                        (2, "Wednesday"), 
                                        (3, "Thursday"), 
                                        (4, "Friday"), 
                                        (5, "Saturday"), 
                                        (6, "Sunday")], validators=[InputRequired()])
    dishDescription = TextAreaField('Description: ')
    allergins=SelectMultipleField('Allergens (if any)', 
                                choices=[('not applicable','Not applicable'),
                                ('gluten','Gluten'),
                                ('dairy','Dairy'),
                                ('nut','Nut'),
                                ('soya','Soya'),
                                ('egg','Egg')], option_widget=CheckboxInput(),
                                validators=[InputRequired()])
    dishPic = FileField('Upload a picture:', validators=[FileRequired(), FileAllowed(['jpg','png'],'Images Only!')])
    ingredients= TextAreaField('List the ingredients needed',default="In the format: ingredient1, ingredient2... each ingredient is separated by a comma!")
    submit = SubmitField('Submit')

    def validate_allergins(form, field):
        if 'not applicable' in field.data and len(field.data) > 1:
            form.allergins.errors.append('You cannot select "Not applicable" along with other options.')


class UserPic(FlaskForm):
    profile_pic = FileField('Upload a cover', validators=[FileRequired(),FileAllowed(['jpg','png'],'Images Only!')])
    submit = SubmitField('Enter')

class cardDetails(FlaskForm):
    cardNum = IntegerField('Enter card number:', validators=[InputRequired()])
    cardHolder = StringField('Enter card holders name:', validators=[InputRequired()])
    cvv = IntegerField('Cvv', validators= [InputRequired()])
    tableNum = IntegerField('Table Youre sitting at:', validators=[InputRequired()])
    submit = SubmitField('Enter')

class submitModifications(FlaskForm):
    submit = SubmitField('Enter')
    
class Review(FlaskForm):
    comment = StringField('Additional Comments: ')
    submit = SubmitField('Enter')
    
class makeBooking(FlaskForm):
    name = StringField("Reservation Name: ", validators=[InputRequired()])
    date = StringField("Date (DD-MM-YY): ", validators=[InputRequired()])
    time = IntegerField("Time (XX:00):", validators=[InputRequired(), NumberRange(0,23)])
    
    submit = SubmitField("Make Reservation")
    
class StockForm(FlaskForm):
    ingredient=SelectMultipleField('Ingredient:',validators=[InputRequired()])
    date = DateField("Expiry Date:", validators=[InputRequired()])
    quantity = IntegerField("Quantity:", validators=[InputRequired() ])
    submit = SubmitField('Submit')

class Supplier(FlaskForm):
    email = StringField()
    id = IntegerField()

class EditSupplier(FlaskForm):
    email = StringField()
    id = IntegerField()