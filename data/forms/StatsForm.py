from flask_wtf import FlaskForm
from wtforms import (DateField, FileField, IntegerField, StringField,
                     SubmitField)
from wtforms.validators import Length, NumberRange


class StatsForm(FlaskForm):
    weight = IntegerField('Вес', default=0, validators=[NumberRange(min=1)])
    height = IntegerField('Рост', default=0, validators=[NumberRange(min=1)])
    birthday = DateField('Дата рождения')
    submit = SubmitField('Изменить')
