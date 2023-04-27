from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class AnswerTaskForm(FlaskForm):
    answer = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Отправить')
