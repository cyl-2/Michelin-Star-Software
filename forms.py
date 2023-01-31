from wtforms import SubmitField, IntegerField, SelectField, StringField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange

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