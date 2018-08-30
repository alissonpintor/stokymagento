from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField, IntegerField
from wtforms import DateTimeField
from wtforms.validators import DataRequired
from app.core.forms import widgets as w


class ConfigForm(FlaskForm):
    """
    Formulario para alteração dos dados de Configuração do sistema
    """

    configId = HiddenField('ID', default=0)
    baseURL = StringField('URL Base', widget=w.GeInputWidget(), validators=[DataRequired()])

    submit = SubmitField('Atualizar')


class ConfigMagentoForm(FlaskForm):
    """
    Formulario para alteração dos dados de Configuração de acesso
    da API do magento
    """

    config_id = HiddenField('ID', default=0)
    api_url = StringField(
        'URL Base', 
        widget=w.GeInputWidget(), 
        validators=[DataRequired()]
    )
    api_user = StringField(
        'User', 
        widget=w.GeInputWidget(), 
        validators=[DataRequired()]
    )
    api_pass = StringField(
        'Password', 
        widget=w.GeInputWidget(), 
        validators=[DataRequired()]
    )
    magento_version = StringField(
        'Versão do Magento', 
        widget=w.GeInputWidget()
    )
    categoria_default = IntegerField(
        'Categoria Default', 
        widget=w.GeIntegerWidget()
    )
    dtsincr_estoque = DateTimeField(
        'Sincronizaçao Estoque',
        format='%d/%m/%Y %H:%M:%S', 
        widget=w.GeDateTimeWidget()
    )

    submit = SubmitField('Atualizar')
