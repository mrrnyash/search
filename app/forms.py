from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
from app.models import User

class SearchForm(FlaskForm):
    request = StringField('Запрос', validators=[DataRequired()])
    submit = SubmitField('Найти')

class FilterForm(FlaskForm):
    pass

class RegistrationForm(FlaskForm):
    username = StringField('Логин', [Length(min=4, max=25)])
    email = StringField('Email', [Length(min=6, max=35)])
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другой логин')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста используйте другой Email')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')