import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, EmailField
from wtforms import BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class DepartamentForm(FlaskForm):
    title = StringField("Название департамента", validators=[DataRequired()])
    chief = IntegerField("Глава", validators=[DataRequired()])
    members = StringField("id участников через ', '", validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Применить')
