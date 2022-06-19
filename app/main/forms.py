from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import Optional, DataRequired, ValidationError
from app.models import SourceDatabase, DocumentType
from flask import request


class SearchForm(FlaskForm):
    q = StringField('', validators=[], render_kw={'placeholder': 'Поисковый запрос'})

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)

    title = StringField('Заглавие', validators=[Optional()], render_kw={'placeholder': 'Заглавие'})
    author = StringField('Автор', validators=[Optional()], render_kw={'placeholder': 'Автор'})
    journal_title = StringField('Название журнала', validators=[Optional()],
                                render_kw={'placeholder': 'Название журнала'})
    isbn_issn_doi = StringField('ISBN/ISSN/DOI', validators=[Optional()], render_kw={'placeholder': 'ISBN/ISSN/DOI'})
    keywords = StringField('Ключевые слова', validators=[Optional()], render_kw={'placeholder': 'Ключевые слова'})
    pubyear1 = IntegerField('Опубликован от', validators=[Optional()], render_kw={'placeholder': 'От'})
    pubyear2 = IntegerField('До', validators=[Optional()], render_kw={'placeholder': 'До'})
    source_database = QuerySelectMultipleField(
        'База данных',
        query_factory=lambda: SourceDatabase.query.all(),
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    document_type = QuerySelectMultipleField(
        'Тип документа',
        query_factory=lambda: DocumentType.query.all(),
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    )
    submit = SubmitField('Поиск')

    def validate_pubyear(self, pubyear1, pubyear2):
        if pubyear1 > pubyear2:
            raise ValidationError('Дата публикации задана неверно')


class ReportForm(FlaskForm):
    report_type = SelectField(u'Тип отчета', choices=[('type_1', 'Для одной базы данных'),
                                                      ('type_2', 'Для всех баз данных'),
                                                      ('type_3', 'Для ключевых слов')],
                                                        validators=[DataRequired()])
    source_database = SelectField(u'', choices=[('Издательство Лань', 'ЭБС Лань'),
                                                      ('ИКО Юрайт', 'ЭБС Юрайт'),
                                                      ('RUCONT', 'ЭБС Руконт')],
                                                        validators=[Optional()])
    date_1 = DateField(u'От', format='%d.%m.%Y')
    date_2 = DateField(u'До', format='%d.%m.%Y')
    submit = SubmitField('Сформировать отчет')



