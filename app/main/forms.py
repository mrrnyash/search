from flask_wtf import FlaskForm
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import Optional
from app.models import SourceDatabase, DocumentType


class SearchForm(FlaskForm):
    search_request = StringField('', render_kw={'placeholder': 'Поисковый запрос'})
    title = StringField('Заглавие', validators=[Optional()], render_kw={'placeholder': 'Заглавие'})
    author = StringField('Автор', validators=[Optional()], render_kw={'placeholder': 'Автор'})
    journal_title = StringField('Название журнала', validators=[Optional()],
                                render_kw={'placeholder': 'Название журнала'})
    isbn_issn_doi = StringField('ISBN/ISSN/DOI', validators=[Optional()], render_kw={'placeholder': 'ISBN/ISSN/DOI'})
    keywords = StringField('Ключевые слова', validators=[Optional()], render_kw={'placeholder': 'Ключевые слова'})
    publishing_year_1 = IntegerField('Опубликован от', validators=[Optional()], render_kw={'placeholder': 'От'})
    publishing_year_2 = IntegerField('До', validators=[Optional()], render_kw={'placeholder': 'До'})
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
    submit = SubmitField('Найти')



