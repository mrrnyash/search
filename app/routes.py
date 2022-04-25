from flask import render_template, flash, redirect
from app import app, models, db
from app.forms import SearchForm, LoginForm, RegistrationForm

@app.route('/', methods=['POST', 'GET'])
@app.route('/index')
def index():
   form = SearchForm()
   return render_template('index.html', title='Главная', form=form)

@app.route('/search',  methods=['GET', 'POST'])
def search():
   return render_template('search.html', title='Результаты поиска')



@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      flash('Запрос на вход для пользователя {}, remember_me={}'.format(
         form.username.data, form.remember_me.data))
      return redirect('/index')
   return render_template('login.html', title='Войти', form=form)

