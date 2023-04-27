from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ManualAnswerForm(FlaskForm):
    score = IntegerField(
        'На сколько % выполнено задание:',
        validators=[DataRequired(), NumberRange(min=0, max=100)],
    )
    submit = SubmitField('Готово')
