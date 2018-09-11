from flask import Blueprint, render_template
from flask import redirect, request, url_for, current_app, jsonify
from flask_login import login_required
from datetime import datetime
import locale

# import do db
from app import imageSet, db

# import do log
from app.log import Log

# import od objetos das Entidades do Magento
from app.core.api_magento.product import createProduct, updateImage
from app.core.api_magento.product import updateProduct, productList

# import tasks
from app.application import mycelery
from .tasks import atualiza_precos_task, atualiza_promocoes_task
from .tasks import inativar_task, atualiza_estoque_task, enviar_novos_task

# import das models usadas na view
from app.models.produtos import CissProdutoGrade, MagProduto
from app.models.config import ConfigMagento
from app.models.tasks import MagTasks

# import dos Forms da View
from .forms import EnviarImagemProdutoForm
from .forms import EnviarProdutosNovosForm

# importa as funcionalidades do core
from app.core.image_generator import genImage
from app.core.utils import warning, success
from app.core.utils import read_images

# import dos filtros de dados
from .filter import buscar_produtos_novos, buscar_categorias_produtos
from .filter import buscar_produtos_inativos, buscar_precos_produtos
from .filter import buscar_estoque_produtos, buscar_produtos_promocao
from .filter import buscar_produtos_nao_enviados, atualizar_base


locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
produtos = Blueprint('produtos', __name__)


@login_required
@produtos.route('/nao-enviados')
def listar_nao_enviados():
    """
        Lista os produtos que ainda não foram enviados para o site
    """
    template = 'produtos/lista-produtos-nao-enviados.html'
    produtos = buscar_produtos_nao_enviados()
    imagens = read_images().keys()

    if not produtos:
        warning('Não existem produtos pendentes de serem enviados')

    result = {
        'title': 'Produtos',
        'subtitle': 'Não Enviados',
        'produtos': produtos,
        'imagens': imagens
    }
    return render_template(template, **result)


@login_required
@produtos.route('/imagens/enviar', methods=['GET', 'POST'])
def enviar_imagem():
    """
        Envia as imagens dos produtos
    """
    template = 'produtos/form-enviar-imagem.html'

    if current_app.config['UPLOADS_DEFAULT_URL'] is None:
            warning('A URL Base do Sistema não está configurada. ' +
                    'Configure-a para que as imagens possam ser salvas.')
            return redirect(url_for('integrador.produtos_enviar_imagem'))

    if request.method == 'POST':
        import os

        base_path = os.getcwd() + '/uploads/photos/'
        imagem = request.files['file']
        nome = imagem.filename
        filepath = base_path + nome

        if nome == '':
            return 'Nenhuma Imagem Foi Selecionada', 400

        if nome.rfind('.') == -1:
            return 'O arquivo informado não possui extensão definida', 400

        ext = nome.split('.')[1].lower()
        if not imageSet.extension_allowed(ext):
            return 'A extensão informada não é válida', 400

        if not validar_nome_imagem(nome):
            return 'O nome da imagem precisa ser um codigo válido', 400

        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)

        image = imageSet.save(imagem)
        image = base_path + image
        genImage(image, image)

        # busca o cadastro do produto e se existir altera para atualizar imagem
        sku = int(nome.split('.')[0])
        produto = MagProduto.by(sku=sku)
        if produto:
            produto.atualiza_imagem = True
            produto.possui_imagem = True
            produto.update()

        Log.info(f'[ENVIAR IMAGEM] Enviado Imagem do produto {nome}.')

    result = {
        'title': 'Enviar Imagens Produtos'
    }
    return render_template(template, **result)


@login_required
@produtos.route('/enviar', methods=['GET', 'POST'])
def enviar_novos():
    """
        Envia os produtos novos para o site
    """

    template = 'produtos/form-enviar-produtos.html'
    form = EnviarProdutosNovosForm()
    imagens = read_images().keys()

    task = current_app.enviar_novos_task
    clear_task = request.args.get('clear_task', None)
    if clear_task and clear_task == 'yes' and task.state == 'SUCCESS':
        current_app.enviar_novos_task = task = None

    produtos = None
    if not task:
        produtos = buscar_produtos_novos()

    if not produtos and not task:
        warning('Não existem produtos para serem enviados para o site')

    categorias = buscar_categorias_produtos()
    if not categorias:
        warning('Não existem categorias do site cadastradas')

    if form.validate_on_submit() and produtos and categorias:
        produtos_task = {}

        for p in produtos:
            secao = int(request.form.get(f'secao-{p.idsubproduto}', 0))
            grupo = int(request.form.get(f'grupo-{p.idsubproduto}', 0))
            subgrupo = int(request.form.get(f'subgrupo-{p.idsubproduto}', 0))

            if secao and grupo and subgrupo:
                categorias = [secao, grupo, subgrupo]
                produtos_task[p.idsubproduto] = categorias

        task = enviar_novos_task.apply_async(args=(produtos_task,))
        current_app.enviar_novos_task = task

        success(f'Tarefa iniciada com sucesso')
        return redirect(url_for('produtos.enviar_novos'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Enviar Novos',
        'form': form,
        'imagens': imagens,
        'produtos': produtos,
        'categorias': categorias,
        'task': task
    }
    return render_template(template, **result)


@login_required
@produtos.route('/enviar/categorias/<id>')
def buscar_categorias(id):
    """
        Utilizado na tela de envio de novos produtos para
        buscar as categorias dos produtos
    """
    categorias = buscar_categorias_produtos(id)
    categorias = [c.json() for c in categorias]

    return jsonify(categorias)


@login_required
@produtos.route('/estoque/atualizar', methods=['GET', 'POST'])
def atualiza_estoque():
    """
        Atualiza o estoque dos produtos no site
    """

    template = 'produtos/form-atualiza-estoque.html'
    form = EnviarProdutosNovosForm()
    config = ConfigMagento.by_id(1)

    task = current_app.atualiza_estoque_task
    clear_task = request.args.get('clear_task', None)
    if clear_task and clear_task == 'yes' and task.state == 'SUCCESS':
        current_app.atualiza_estoque_task = task = None

    produtos = None
    if not task:
        produtos = buscar_estoque_produtos(dthr_sincr=config.dtsincr_estoque)

    if form.validate_on_submit() and produtos:
        task = atualiza_estoque_task.apply_async()
        current_app.atualiza_estoque_task = task

        success(f'Tarefa iniciada com sucesso')
        return redirect(url_for('produtos.atualiza_estoque'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Atualizar Estoque',
        'form': form,
        'produtos': produtos,
        'task': task
    }
    return render_template(template, **result)


@login_required
@produtos.route('/precos/atualizar', methods=['GET', 'POST'])
def atualiza_precos():
    """
        Atualiza os preços dos produtos no site
    """

    template = 'produtos/form-envia-precos.html'
    config = ConfigMagento.by_id(1)

    task = current_app.atualiza_precos_task
    clear_task = request.args.get('clear_task', None)
    if clear_task and clear_task == 'yes' and task.state == 'SUCCESS':
        current_app.atualiza_precos_task = task = None

    produtos = None
    if not task:
        produtos = buscar_precos_produtos(dthr_sincr=config.dtsincr_preco)

    form = EnviarProdutosNovosForm()

    if form.validate_on_submit() and produtos:
        task_id = atualiza_precos_task.apply_async()
        current_app.atualiza_precos_task = task_id

        success(f'Tarefa iniciada com sucesso')
        return redirect(url_for('produtos.atualiza_precos'))

    result = {
        'title': 'Produtos:',
        'subtitle': 'Atualizar Preços',
        'produtos': produtos,
        'task': task,
        'form': form
    }
    return render_template(template, **result)


@login_required
@produtos.route('/promocoes', methods=['GET', 'POST'])
def atualiza_promocoes():
    """
        Envia os produtos em promoção para o site
    """

    template = 'produtos/form-envia-promocoes.html'
    config = ConfigMagento.by_id(1)

    task = current_app.atualiza_promocoes_task
    clear_task = request.args.get('clear_task', None)
    if clear_task and clear_task == 'yes' and task.state == 'SUCCESS':
        current_app.atualiza_promocoes_task = task = None

    produtos = None
    if not task:
        produtos = buscar_produtos_promocao(dthr_sincr=config.dtsincr_promocao)

    form = EnviarProdutosNovosForm()

    if form.validate_on_submit():
        task = atualiza_promocoes_task.apply_async()
        current_app.atualiza_promocoes_task = task

        success(f'Tarefa iniciada com sucesso')
        return redirect(url_for('produtos.atualiza_promocoes'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Atualizar Promoções',
        'produtos': produtos,
        'task': task,
        'form': form
    }
    return render_template(template, **result)


@login_required
@produtos.route('/inativar', methods=['GET', 'POST'])
def inativar():
    """
        Inativa os produtos no site
    """

    template = 'produtos/form-inativar-produtos.html'

    task = current_app.inativar_task
    clear_task = request.args.get('clear_task', None)
    if clear_task and clear_task == 'yes' and task.state == 'SUCCESS':
        current_app.inativar_task = task = None

    produtos = None
    if not task:
        produtos = buscar_produtos_inativos()

    form = EnviarProdutosNovosForm()

    if form.validate_on_submit() and produtos:
        task = inativar_task.apply_async()
        current_app.inativar_task = task

        success(f'Tarefa iniciada com sucesso')
        return redirect(url_for('produtos.inativar'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Inativar',
        'form': form,
        'produtos': produtos,
        'task': task
    }
    return render_template(template, **result)


@login_required
@produtos.route('/base/atualizar', methods=['GET', 'POST'])
def atualiza_base():
    """
        Atualiza a base de dados com produtos ja enviados
    """
    template = 'produtos/form-atualiza-base.html'
    form = EnviarProdutosNovosForm()

    if form.validate_on_submit():
        produtos = productList()
        atualizar_base(produtos)

        success('Base atualizada com sucesso')
        return redirect(url_for('produtos.atualiza_base'))

    result = {
        'title': 'Atualizar Estoque Produtos',
        'form': form,
        'produtos': None
    }
    return render_template(template, **result)


def validar_nome_imagem(filename):
    """
        Verifica se o nome da imagem é um inteiro válido
        representando o codigo de um produto e se ele
        existe no banco de dados do ERP
    """

    nome_imagem = filename.split('.')[0]

    if nome_imagem.isdigit():
        produto = CissProdutoGrade.query.filter_by(idsubproduto=nome_imagem)
        produto = produto.first()
        if produto:
            return True

    return False


@login_required
@produtos.route('/task/<id>', methods=['GET'])
def get_task(id):
    """
        Retorna a task a partir do id
    """

    task = mycelery.AsyncResult(id)

    if task.info:
        return jsonify({
            'id': task.id,
            'name': task.info['name'],
            'total': task.info['total'],
            'current': task.info['current'],
            'complete': task.info['complete'],
            'errors': task.info['errors'],
            'errors_count': task.info['errors_count'],
            'status': task.info['status']
        })

    return 'Não existem dados', 400
