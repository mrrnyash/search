from flask import render_template
from app import app
from app.forms import SearchForm, LoginForm

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
   return render_template('login.html', title='Войти', form=form)