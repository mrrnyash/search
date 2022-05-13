from flask import render_template, redirect, url_for, \
    request, current_app
from app.main.forms import SearchForm, FileForm
from app.models import User, Record
from app.main import bp
from flask_login import login_required
from flask import g
from app import db

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
    # return '<h1>{}</h1>'.format(g.search_form.data)


@bp.route('/admin')
@login_required
def admin():
    return render_template(
        'administration.html',
        title='Администрирование',
    )


@bp.route('/control', methods=['GET', 'POST'])
@login_required
def control():
    form = FileForm()
    return render_template(
        'control.html',
        title='Панель управления',
        form=form
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
