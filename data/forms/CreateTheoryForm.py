from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewTheoryForm(FlaskForm):
    title = StringField('Название урока', validators=[DataRequired(), Length(max=300)])
    description = TextAreaField("Описание")
    video = FileField('Видео')
    picture = FileField("Картинка")
    submit = SubmitField('Загрузить')
