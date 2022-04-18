from flask import render_template
from app import app
from app.forms import SearchForm

@app.route('/',methods=['POST', 'GET'])
@app.route('/index')
def index():
   form = SearchForm()
   return render_template('index.html', title='Главная', form=form)