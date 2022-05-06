from flask import render_template, flash, redirect, url_for, \
    request, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import SearchForm, LoginForm, RegistrationForm
from app.models import *
from werkzeug.urls import url_parse
from app.search import Search


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        session['formdata'] = form.data
        return redirect(url_for('search'))
    return render_template(
        'index.html',
        title='Главная',
        form=form
    )

@app.route('/search', methods=['GET', 'POST'])
def search():
    formdata = session.get('formdata', None)
    page = request.args.get('page', 1, type=int)
    num_records = Record.query.filter(
        Record.title.like('%{}%'.format(formdata['search_request']))).count()
    records = Record.query.filter(
        Record.title.like('%{}%'.format(formdata['search_request']))).paginate(
        page, app.config['RECORDS_PER_PAGE'], False)
    next_url = url_for('search', page=records.next_num) \
        if records.has_next else None
    prev_url = url_for('search', page=records.prev_num) \
        if records.has_prev else None
    return render_template(
        'index.html',
        title='Поиск',
        records=records.items,
        next_url=next_url,
        prev_url=prev_url,
        num_records=num_records
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if user.role_id == 1:
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('admin')
            return redirect(next_page)
        else:
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('control')
            return redirect(next_page)
    return render_template(
        'login.html',
        title='Вход',
        form=form
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user_role = UserRole.query.filter_by(name=form.user_role.data).first()
        if user_role is not None:
            db.session.add(user_role)
            user.role.append(user_role)
        else:
            user_role = UserRole(name=form.user_role.data)
            db.session.add(user_role)
            user.role.append(user_role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно')
        return redirect(url_for('login'))
    return render_template(
        'register.html',
        title='Регистрация в системе',
        form=form)


@app.route('/admin')
@login_required
def admin():
    sum_records = Record.query.count()
    return render_template(
        'admin_panel.html',
        title='Панель управления администратора',
        sum_records=sum_records
    )


@app.route('/control')
@login_required
def control():
    sum_records = Record.query.count()
    return render_template(
        'control.html',
        title='Панель управления',
        sum_records=sum_records
    )


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'user.html',
        user=user,
        title='Учетная запись'
    )
