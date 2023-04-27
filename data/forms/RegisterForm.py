from flask_wtf import FlaskForm
from wtforms import (EmailField, IntegerField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, NumberRange


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    group_id = IntegerField(
        'Укажите номер группы, выданный вам учителем',
        validators=[DataRequired(), NumberRange(min=1, max=100)],
    )
    submit = SubmitField('Через тернии к звёздам!')
