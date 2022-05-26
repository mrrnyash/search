from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length, EqualTo
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField('', [Length(min=4, max=25), DataRequired()], render_kw={'placeholder': 'Логин'})
    email = StringField('', [Length(min=6, max=35), DataRequired()], render_kw={'placeholder': 'Email'})
    password = PasswordField('', validators=[DataRequired()], render_kw={'placeholder': 'Пароль'})
    password2 = PasswordField(
        '',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={'placeholder': 'Повторите пароль'}
    )
    user_role = SelectField(u'', choices=[('administrator', 'Администратор'), ('selector', 'Комплектатор')],
                            validators=[DataRequired()])
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
    username = StringField('', validators=[DataRequired()], render_kw={'placeholder': 'Логин'})
    password = PasswordField('', validators=[DataRequired()], render_kw={'placeholder': 'Пароль'})
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
