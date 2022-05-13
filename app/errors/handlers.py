from flask import render_template
from app import db
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html', title='Ошибка 404'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='Ошибка 500'), 500


@bp.app_errorhandler(413)
def too_large(error):
    return render_template('errors/413.html', title='Ошибка 413'), 413