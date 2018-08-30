from flask_wtf import FlaskForm
from wtforms import SubmitField


class ImportarCategoriaForm(FlaskForm):
    """
    Formulario para importar as categorias 
    dos produtos categorias do site
    """

    submit = SubmitField('Importar')