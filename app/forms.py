from flask_wtf import FlaskForm
from flask_bootstrap5 import Bootstrap
from wtforms import StringField, SubmitField, BooleanField, PasswordField, validators


class SearchForm(FlaskForm):
    request = StringField('Запрос', validators=[validators.DataRequired()])
    submit = SubmitField('Найти')

class FilterForm(FlaskForm):
    pass

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('Новый пароль', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Пароль должен совпадать')
    ])
    confirm = PasswordField('Повторить пароль')
    accept_tos = BooleanField('Я принимаю лицензионное соглашение', [validators.DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[validators.DataRequired()])
    password = PasswordField('Пароль', validators=[validators.DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')