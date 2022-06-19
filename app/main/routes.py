import os
from flask import render_template, redirect, url_for, \
    request, current_app, abort, g, send_from_directory
from app.main.forms import SearchForm, ReportForm
from app.main import bp
from flask_login import login_required
from app import db
from werkzeug.utils import secure_filename
from app.models import Record, User
from app.upload import DBLoader
from app.report import Report

# from multiprocessing import Pool, cpu_count


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


@bp.route('/search/author=<author>')
@bp.route('/search/author=<author>&page=<int:page>')
def search_by_author(author, page=1):
    record_query = Record.query.filter(
        Record.authors.any(name=author)).paginate(page, current_app.config['RECORDS_PER_PAGE'], False)
    total = record_query.total
    records = record_query.items
    next_url = url_for('main.search_by_author',
                       q=g.search_form.q.data,
                       author=author,
                       title=g.search_form.title.data,
                       isbn_issn_doi=g.search_form.isbn_issn_doi.data,
                       keywords=g.search_form.keywords.data,
                       pubyear1=g.search_form.pubyear1.data,
                       pubyear2=g.search_form.pubyear2.data,
                       source_database=g.search_form.source_database.data,
                       document_type=g.search_form.document_type.data,
                       page=page + 1) \
        if total > page * current_app.config['RECORDS_PER_PAGE'] else None
    prev_url = url_for('main.search_by_author', q=g.search_form.q.data,
                       author=author,
                       title=g.search_form.title.data,
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
        records=records,
        title='Поиск',
        next_url=next_url,
        prev_url=prev_url,
        form=g.search_form,
        total=total
    )


@bp.route('/search/publisher=<publisher>')
@bp.route('/search/publisher=<publisher>&page=<int:page>')
def search_by_publisher(publisher, page=1):
    record_query = Record.query.filter(
        Record.publisher.any(name=publisher)).paginate(page, current_app.config['RECORDS_PER_PAGE'], False)
    total = record_query.total
    records = record_query.items
    next_url = url_for('main.search_by_publisher',
                       publisher=publisher,
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
    prev_url = url_for('main.search_by_publisher',
                       publisher=publisher,
                       q=g.search_form.q.data,
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
        records=records,
        title='Поиск',
        next_url=next_url,
        prev_url=prev_url,
        form=g.search_form,
        total=total
    )


@bp.route('/search/year=<year>')
@bp.route('/search/year=<year>&page=<int:page>')
def search_by_year(year, page=1):
    record_query = Record.query.filter_by(publishing_year=year).paginate(page, current_app.config['RECORDS_PER_PAGE'],
                                                                         False)
    total = record_query.total
    records = record_query.items
    next_url = url_for('main.search_by_year',
                       year=year,
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
    prev_url = url_for('main.search_by_year',
                       year=year,
                       q=g.search_form.q.data,
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
        records=records,
        title='Поиск',
        next_url=next_url,
        prev_url=prev_url,
        form=g.search_form,
        total=total
    )


@bp.route('/control')
@login_required
def control():
    return render_template(
        'control.html',
        title='Панель управления'
    )


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    loader = DBLoader()
    for uploaded_file in request.files.getlist('file'):
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['ALLOWED_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    loader.upload_to_database()
    errors = loader.get_upload_errors()
    if errors is not None:
        return render_template('upload.html',
                               title='Загрузка файлов',
                               errors=errors)
    return render_template('upload.html',
                           title='Загрузка файлов')


@bp.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = ReportForm()
    r = Report()

    if form.validate_on_submit():
        data = ['This', 'is', 'a', 'test']
        r.generate(data)
        send_from_directory(directory=current_app.config['REPORT_FOLDER'], filename='Report.csv')
        # redirect(url_for('main.report'))
    return render_template('report.html',
                           title='Отчет',
                           form=form
                           )


@bp.route('/admin')
@login_required
def admin():
    return render_template(
        'admin.html',
        title='Консоль администратора',
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
