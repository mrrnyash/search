from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    request = StringField('Запрос',validators=[DataRequired()])
    submit = SubmitField('Поиск')