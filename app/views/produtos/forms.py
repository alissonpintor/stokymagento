from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms import FileField
from wtforms.validators import DataRequired, EqualTo
from app.core.forms import widgets as w


class ImportarCategoriaForm(FlaskForm):
    """
    Formulario para importar as categorias 
    dos produtos categorias do site
    """

    submit = SubmitField('Importar')


class CadastrarCategoriaForm(FlaskForm):
    """
    Formulario para cadastrar categorias dos produtos de
    acodordo com as categorias do site
    """
    kwargs = {'validators': [DataRequired()], 'widget': w.GeIntegerWidget()}
    
    idproduto = IntegerField('Codigo', **kwargs)
    secao = IntegerField('Seção', **kwargs)
    grupo = IntegerField('Grupo', **kwargs)
    subgrupo = IntegerField('SubGrupo', **kwargs)

    submit = SubmitField('Cadastrar')


class CadastrarListaCategoriaForm(FlaskForm):
    """
    Formulario para cadastrar categorias dos produtos de
    acodordo com as categorias do site
    """

    lista = FileField(
        'Lista CSV', validators=[DataRequired()], widget=w.GeFileWidget())
    submit = SubmitField('Enviar')


class EnviarImagemProdutoForm(FlaskForm):
    """
    Formulario para cadastrar categorias dos produtos de
    acodordo com as categorias do site
    """

    imagem = FileField('Imagem')
    submit = SubmitField('Enviar')


class EnviarProdutosNovosForm(FlaskForm):
    """
    Formulario para enviar produtos novos
    para o site
    """

    enviar = SubmitField('Enviar')
