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
from app.core.tasks import enviar_produtos_task

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
from .filter import buscar_data_estoque_produtos, buscar_produtos_promocao
from .filter import buscar_produtos_nao_enviados, atualizar_base

# import dos conversores de objetos magento
from .convert import converte_precos_produtos, converteProduto
from .convert import converte_produtos_promocao, converte_produtos_estoque
from .convert import converte_produto_inativo


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

    produtos = buscar_produtos_novos()
    if not produtos:
        warning('Não existem produtos para serem enviados para o site')

    categorias = buscar_categorias_produtos()
    if not categorias:
        warning('Não existem categorias do site cadastradas')

    if form.validate_on_submit() and produtos and categorias:
        enviados = 0

        Log.info(f'[ENVIAR NOVO] Iniciando envio dos produtos.')
        for produto in produtos:
            secao = int(request.form.get(f'secao-{produto.idsubproduto}', 0))
            grupo = int(request.form.get(f'grupo-{produto.idsubproduto}', 0))
            subgrupo = int(request.form.get(f'subgrupo-{produto.idsubproduto}', 0))

            if secao and grupo and subgrupo:
                Log.info(f'[ENVIAR NOVO] Iniciando envio do item {produto.idsubproduto}.')

                categorias = [secao, grupo, subgrupo]
                data = converteProduto(produto, categorias)
                try:
                    Log.info(f'[ENVIAR NOVO]------ Enviado para o site')
                    createProduct(
                        data['sku'],
                        'simple',
                        '4',
                        data['data']
                    )
                    updateImage(
                        data['image'],
                        data['sku'],
                        data['sku']
                    )

                    # altera o tipo do produto como enviado no erp
                    Log.info(f'[ENVIAR NOVO]------ Salvando alterações no ERP')
                    produto.idtipo = 2
                    produto.update()

                    Log.info(f'[ENVIAR NOVO]------ Salvando alterações no Integrador')
                    mag_produto = MagProduto.by(sku=produto.idsubproduto)
                    if not mag_produto:
                        mag_produto = MagProduto()
                        mag_produto.sku = produto.idsubproduto

                    mag_produto.idsecao = categorias[0]
                    mag_produto.idgrupo = categorias[1]
                    mag_produto.idsubgrupo = categorias[2]

                    # salva se o produto possui imagem ou nao
                    possui_imagem = True if produto.idsubproduto in imagens else False
                    mag_produto.atualiza_imagem = not possui_imagem
                    mag_produto.possui_imagem = possui_imagem
                    mag_produto.update()

                    enviados += 1

                except Exception as e:
                    Log.error(f'[ENVIAR NOVO] Erro ao enviar o produto {p.idsubproduto} erro: {e}')

        Log.info(f'[ENVIAR NOVO] Envio Finalizado.')

        success(f'Foram enviados {enviados} item(s) para serem processados.')
        return redirect(url_for('produtos.enviar_novos'))

    result = {
        'title': 'Enviar Produtos Novos',
        'form': form,
        'imagens': imagens,
        'produtos': produtos,
        'categorias': categorias
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
    datahora_atual = datetime.now()
    produtos = buscar_data_estoque_produtos(dthr_sincr=config.dtsincr_estoque)

    if form.validate_on_submit() and produtos:
        Log.info(f'[ATUALIZAR ESTOQUE] Iniciando envio dos produtos.')

        mag_produtos = converte_produtos_estoque(produtos)
        total = len(mag_produtos)
        atualizados = 0

        for p in mag_produtos:
            try:
                Log.info(f"[ATUALIZAR ESTOQUE] Iniciando envio do item {p['sku']}.")
                updateProduct(
                    sku=p['sku'],
                    data=p['data']
                )
                Log.info(f'[ATUALIZAR ESTOQUE]------ Enviado para o site')
                atualizados += 1
            
            except Exception as e:
                Log.error(
                    f'[ATUALIZAR ESTOQUE] Erro ao enviar o produto {p["sku"]} erro: {e}')

        Log.info(f'[ATUALIZAR ESTOQUE]------ Salvando alterações no Integrador')
        config.dtsincr_estoque = datahora_atual
        config.update()
        Log.info(f'[ATUALIZAR ESTOQUE] Envio Finalizado.')

        success(f'Foram atualizados {atualizados} item(s) de {total}')
        return redirect(url_for('produtos.atualiza_estoque'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Atualizar Estoque',
        'form': form,
        'produtos': produtos
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
    dthr_sincr = datetime.now()
    produtos = buscar_precos_produtos(dthr_sincr=config.dtsincr_preco)
    form = EnviarProdutosNovosForm()

    if form.validate_on_submit() and produtos:
        Log.info(f'[PREÇO] Iniciando o envio dos produtos.')

        mag_produtos = converte_precos_produtos(produtos)
        total = len(mag_produtos)
        atualizados = 0

        for p in mag_produtos:
            try:
                Log.info(f'[PREÇO] Iniciando o envio do item {p["sku"]}.')
                updateProduct(
                    sku=p['sku'],
                    data=p['data']
                )
                Log.info(f'[PREÇO]------ Enviado para o site')
                atualizados += 1

            except Exception as e:
                Log.error(
                    f'[PREÇO] Erro ao enviar o produto {p["sku"]} erro: {e}')

        Log.info(f'[PREÇO] Envio de produtos finalizado.')
        Log.info(f'[PREÇO] Salvando data e hora da sincronização.')
        config.dtsincr_preco = dthr_sincr
        config.update()

        success(f'Foram atualizados {atualizados} item(s) de {total}')
        return redirect(url_for('produtos.atualiza_precos'))

    result = {
        'title': 'Produtos:',
        'subtitle': 'Atualizar Preços',
        'produtos': produtos,
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
    produtos = buscar_produtos_promocao(dthr_sincr=config.dtsincr_promocao)
    dthr_sincr = datetime.now()
    form = EnviarProdutosNovosForm()

    if form.validate_on_submit():
        Log.info(f'[PROMOÇÃO] Iniciando o envio dos produtos.')

        mag_produtos = converte_produtos_promocao(produtos)
        total = len(mag_produtos)
        atualizados = 0

        for p in mag_produtos:
            Log.info(f'[PROMOÇÃO] Iniciando o envio do item {p["sku"]}.')
            try:
                updateProduct(
                    p['sku'],
                    p['data']
                )
                Log.info(f'[PROMOÇÃO]------ Enviado para o site')
                atualizados += 1

            except Exception as e:
                Log.error(
                    f'[PREÇO] Erro ao enviar o produto {p["sku"]} erro: {e}')

        Log.info(f'[PROMOÇÃO] Envio de produtos finalizado.')
        Log.info(f'[PROMOÇÃO] Salvando data e hora da sincronização.')
        config.dtsincr_promocao = dthr_sincr
        config.update()

        success(f'Foram atualizados {atualizados} item(s) de {total}')
        return redirect(url_for('produtos.atualiza_promocoes'))

    result = {
        'title': 'Produtos',
        'subtitle': 'Atualizar Promoções',
        'produtos': produtos,
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
    form = EnviarProdutosNovosForm()
    produtos = buscar_produtos_inativos()

    if form.validate_on_submit() and produtos:
        Log.info(f'[INATIVAR] Iniciando atualizaçao dos produtos.')

        for p in produtos:
            Log.info(f'[INATIVAR] Iniciando atualização do item {p.idsubproduto}.')

            try:
                Log.info(f'[INATIVAR]------ Enviado para o site')
                produto = converte_produto_inativo(p)
                updateProduct(
                    sku=produto['sku'],
                    data=produto['data']
                )

                mag_produto = MagProduto.by(sku=p.idsubproduto)
                if mag_produto:
                    Log.info(f'[INATIVAR]------ Salvando alterações no Integrador')
                    mag_produto.inativo = True
                    db.session.add(mag_produto)
                    db.session.commit()

            except Exception as e:
                Log.error(f'[INATIVAR] Erro ao enviar o produto {p.idsubproduto} erro: {e}')

        Log.info(f'[INATIVAR] Finalizando atualizaçao dos produtos.')

    result = {
        'title': 'Inativar Produtos',
        'form': form,
        'produtos': produtos
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
