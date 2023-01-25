from wtforms import SubmitField, IntegerField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange

class TableForm(FlaskForm):
    table_number = IntegerField( validators=[InputRequired(), NumberRange(1,100)])
    seats = IntegerField(validators=[InputRequired(), NumberRange(1,25)])
    x = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    y = IntegerField(validators=[InputRequired(), NumberRange(0,500)])
    submit = SubmitField("Create Table")