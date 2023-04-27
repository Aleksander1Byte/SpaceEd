from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, DateField, IntegerField
from wtforms.validators import NumberRange, Length


class StatsForm(FlaskForm):
    weight = IntegerField('Вес', default=0,validators=[NumberRange(min=1)])
    height = IntegerField('Рост', default=0, validators=[NumberRange(min=1)])
    birthday = DateField('Дата рождения')
    submit = SubmitField('Изменить')
