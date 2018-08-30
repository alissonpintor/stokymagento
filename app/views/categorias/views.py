from flask import Blueprint, render_template
from flask_login import login_required

# import o log
from app.log import Log

# import das models usadas na view
from app.models.config import ConfigMagento
from app.models.categorias import MagCategorias

# import dos Forms da View
from .forms import ImportarCategoriaForm

# import do data
from .data import registrar_categorias


categorias = Blueprint('categorias', __name__)


@categorias.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    """
        Faz a importação das categorias criadas no site para
        serem usadas no envio de novos produtos
    """

    template = 'categorias/importar/form-importar.html'
    categorias = MagCategorias.by(parent_id=2)
    form = ImportarCategoriaForm()
    config = ConfigMagento.by_id(1)
    has_cat_default = config.categoria_default if config else None

    if form.validate_on_submit() and has_cat_default:
        Log.info(f'[CATEGORIAS] Iniciando a atualização das Categorias.')
        registrar_categorias()
        Log.info(f'[CATEGORIAS] Atualização das Categorias finalizado.')

    result = {
        'title': 'Categorias',
        'subtitle': 'Importar do Site',
        'categorias': categorias,
        'has_cat_default': has_cat_default,
        'tasks': True,
        'form': form
    }
    return render_template(template, **result)