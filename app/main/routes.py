from flask import render_template, redirect, url_for, \
    request, current_app, abort
from app.main.forms import SearchForm
from app.main import bp
from flask_login import login_required
from flask import g
from app import db
from werkzeug.utils import secure_filename
import os
from app.models import Record, User
from app.upload import DBLoader


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    db.session.commit()
    g.sum_records = Record.query.count()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html',
        title='Главная'
    )


@bp.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    records, total = Record.search(g.search_form.data, page,
                                   current_app.config['RECORDS_PER_PAGE'])
    next_url = url_for('main.search',
                       q=g.search_form.q.data,
                       title=g.search_form.title.data,
                       author=g.search_form.author.data,
                       isbn_issn_doi=g.search_form.isbn_issn_doi.data,
                       keywords=g.search_form.keywords.data,
                       pubyear1=g.search_form.pubyear1.data,
                       pubyear2=g.search_form.pubyear2.data,
                       source_database=g.search_form.source_database.data,
                       document_type=g.search_form.document_type.data,
                       page=page + 1) \
        if total > page * current_app.config['RECORDS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data,
                       title=g.search_form.title.data,
                       author=g.search_form.author.data,
                       isbn_issn_doi=g.search_form.isbn_issn_doi.data,
                       keywords=g.search_form.keywords.data,
                       pubyear1=g.search_form.pubyear1.data,
                       pubyear2=g.search_form.pubyear2.data,
                       source_database=g.search_form.source_database.data,
                       document_type=g.search_form.document_type.data,
                       page=page - 1) \
        if page > 1 else None
    return render_template(
        'index.html',
        title='Поиск',
        records=records,
        next_url=next_url,
        prev_url=prev_url,
        form=g.search_form,
        total=total
    )


@bp.route('/admin')
@login_required
def admin():
    return render_template(
        'administration.html',
        title='Администрирование',
    )


@bp.route('/control')
@login_required
def control():
    return render_template(
        'control.html',
        title='Панель управления'
    )


@bp.route('/control', methods=['POST'])
@login_required
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config['ALLOWED_EXTENSIONS']:
            return "Недопустимое разрешение файла", 400
        uploaded_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    DBLoader.load()
    return '', 204


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'user.html',
        user=user,
        title='Учетная запись'
    )
