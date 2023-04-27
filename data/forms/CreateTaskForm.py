from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewTaskForm(FlaskForm):
    question = TextAreaField('Вопрос', validators=[DataRequired(), Length(max=300)])
    picture = FileField("Картинка")
    submit = SubmitField('Загрузить')
