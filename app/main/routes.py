from flask import render_template, redirect, url_for, \
    request, session, current_app
from app.main.forms import SearchForm
from app.models import User, Record
from app.main import bp
from flask_login import login_required


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        session['formdata'] = form.data
        return redirect(url_for('main.search'))
    return render_template(
        'index.html',
        title='Главная',
        form=form
    )


@bp.route('/search', methods=['GET', 'POST'])
def search():
    formdata = session.get('formdata', None)
    page = request.args.get('page', 1, type=int)
    num_records = Record.query.filter(
        Record.title.like('%{}%'.format(formdata['search_request']))).count()
    records = Record.query.filter(
        Record.title.like('%{}%'.format(formdata['search_request']))).paginate(
        page, current_app.config['RECORDS_PER_PAGE'], False)
    next_url = url_for('main.search', page=records.next_num) \
        if records.has_next else None
    prev_url = url_for('main.search', page=records.prev_num) \
        if records.has_prev else None
    return render_template(
        'index.html',
        title='Поиск',
        records=records.items,
        next_url=next_url,
        prev_url=prev_url,
        num_records=num_records
    )


@bp.route('/admin')
@login_required
def admin():
    sum_records = Record.query.count()
    return render_template(
        'admin_panel.html',
        title='Панель управления администратора',
        sum_records=sum_records
    )


@bp.route('/control')
@login_required
def control():
    sum_records = Record.query.count()
    return render_template(
        'control.html',
        title='Панель управления',
        sum_records=sum_records
    )


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'user.html',
        user=user,
        title='Учетная запись'
    )
