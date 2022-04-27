from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, session
from app import app, models, db
from app.forms import SearchForm, LoginForm, RegistrationForm
# NOTE IDK
from app.models import *



@app.route('/')
@app.route('/index')
def index():
   return render_template(
      'index.html', 
      title='Главная', 
      year=datetime.now().year,
   )

@app.route('/search', methods=['GET', 'POST'])
def search():
   form = SearchForm()
   if form.validate_on_submit():
      search_request = form.request.data
      records = db.session.query(Record).filter(Record.title.contains(search_request))
      return render_template(
         'search.html', 
         title='Результаты поиска',
         year=datetime.now().year,
         records=records,
         form=form
         )
   return render_template(
         'search.html', 
         title='Результаты поиска',
         year=datetime.now().year,
         records=records,
         form=form
         )

@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      flash('Запрос на вход для пользователя {}, remember_me={}'.format(
         form.username.data, form.remember_me.data))
      return redirect('/index')
   return render_template(
      'login.html', 
      title='Войти', 
      form=form, 
      year=datetime.now().year
      )
   
@app.route('/about')
def about():
   return render_template(
      'about.html',
      title='О нас',
      year=datetime.now().year,
      message='Разработано специально для Бурятского государственного университета.'
)

