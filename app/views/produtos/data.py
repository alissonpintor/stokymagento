# -*- coding: utf-8 -*-
import os
from datetime import date, timedelta, datetime
from app import db

# import das models
from app.models.config import ConfigMagento
from app.models.categorias import MagCategorias
from app.models.produtos import MagCategoriaProduto, MagErrosProdutos
from app.models.produtos import CissProdutoGrade, MagProduto
from app.models.produtos import CissProdutoEstoque, CissProdutoPreco

# import da API Magento
from app.core.api_magento.category import category_tree
from app.core.api_magento.product import updateProduct
from app.core.api_magento.objects import Stock, Product, Attribute

# import dos utils
from app.core.utils import read_images


class ErrorHandler():
    """
        Manipulador dos erros gerados ao realizar
        as ações na api do magento
    """


def buscarProdutos(codigo=None, inativo=False):
    """
        Query basica dos produtos usado nas buscas
    """
    produto = CissProdutoGrade.query
    produto = produto.filter(CissProdutoGrade.idmodelo == 4)

    if not inativo:
        produto = produto.filter(CissProdutoGrade.flaginativo == 'F')
    else:
        produto = produto.filter(CissProdutoGrade.flaginativo == 'T')
    
    if codigo:
        if type(codigo) is list:
            produto = produto.filter(CissProdutoGrade.idsubproduto.in_(codigo))
        else:
            produto = produto.filter(CissProdutoGrade.idsubproduto == codigo)
    
    return produto


def buscar_produtos_nao_enviados():
    """
        Busca os produtos existentes no ERP que ainda nao foram
        enviados ou marcados para envio
    """
    produto = CissProdutoGrade.query.filter(
        CissProdutoGrade.flaginativo == 'F',
        db.or_(CissProdutoGrade.idmodelo == None, CissProdutoGrade.idmodelo != 4)
    ).order_by(
        CissProdutoGrade.descrresproduto
    ).all()

    return produto


def buscar_produtos_novos(exclude_skus=None):
    """
        Busca os produtos marcados para envio no ERP
    """
    produto = buscarProdutos()
    produto = produto.filter(
        db.or_(CissProdutoGrade.idtipo == None, CissProdutoGrade.idtipo != 2))
    
    if exclude_skus:
        produto = produto.filter(
            CissProdutoGrade.idsubproduto.notin_(exclude_skus)
        )    
    
    produto = produto.order_by(
        CissProdutoGrade.descrresproduto
    )   
    
    return produto


def buscar_categorias_produtos(id = None):
    """
        Busca as seções de produtos cadastradas no site e
        importadas para dentro do sistema

        Params
        ---------
        id: <int> (default=None)

        Returns
        ---------
        categorias: list<MagCategorias>

        Raises
        ---------
    """
    if not id:
        config = ConfigMagento.by_id(1)
        if not config:
            return None        
        id = config.categoria_default
    
    secoes = MagCategorias.query.filter(
        MagCategorias.parent_id == id
    ).order_by(
        MagCategorias.name
    ).all()

    return secoes


def buscar_produtos_inativos():
    """
        Busca os produtos que estao no site e inativos no ERP
    """

    produtos = buscarProdutos(inativo=True)
    produtos = produtos.filter(CissProdutoGrade.idtipo == 2)
    produtos = produtos.order_by(CissProdutoGrade.descrresproduto)
    produtos = produtos.all()[:5]

    return produtos


def converte_produto_inativo(produto):
    """
        Converte o produto no formato magento para enviar ao site
    """

    data = Product(validate_requireds=False)
    data.sku = produto.idsubproduto
    data.status = '0'

    return {
        'sku': str(produto.idsubproduto),
        'data': data.to_soap()
    }


def buscarProdutosEnviadosAtivos():
    """
        Busca os produtos que estao no site e inativos no ERP
    """
    produto = buscarProdutos()
    produto = produto.filter(CissProdutoGrade.idtipo == 2)
    produto = produto.order_by(CissProdutoGrade.descrresproduto)
    produto = produto.all()[:10]
    return produto


def buscar_precos_produtos(dthr_inicial=None):
    """
        Busca os produtos para atualizar os preços no site

        Retorna uma lista com os produtos que teram os preços atualizados
        no site a partir da datahora da ultima atualização. Se a datahora
        não for informada retorna todos os produtos ativos.

        Params
        ----------
        dthr_inicial (datetime, optional)
            Usado para filtrar os produtos com preço alterados a partir da
            datahora informada. Se nao informada retorna todos os produtos
            ativos.

        Returns
        ----------
        produtos (lista<CissProdutoPreco>)
            Retorna a lista com os produtos retornados pela consulta na
            base de dados.
    """

    produtos = CissProdutoPreco.query.join(
        CissProdutoPreco.produto
    ).filter(
        CissProdutoGrade.flaginativo == 'F',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 2
    )

    if dthr_inicial and isinstance(dthr_inicial, datetime):
        produtos = produtos.filter(
            CissProdutoPreco.dtalteracaovar > dthr_inicial)

    produtos = produtos.all()[:5]

    return produtos


def buscar_produtos_promocao(dthr_inicial=None):
    """
        Busca os produtos que estão em promocao no ERP

        Retorna uma lista com os produtos que estão na promoção a 
        partir da datahora da ultima atualização. Se a datahora
        não for informada retorna todos os produtos ativos.

        Params
        ----------
        dthr_inicial (datetime, optional)
            Usado para filtrar os produtos com preço alterados a partir da
            datahora informada. Se nao informada retorna todos os produtos
            ativos.

        Returns
        ----------
        produtos (lista<CissProdutoPreco>)
            Retorna a lista com os produtos retornados pela consulta na
            base de dados.
    """
    dt_hoje = date.today()
    dthr_hoje = datetime.now()

    produtos = CissProdutoGrade.query.join(
        CissProdutoPreco.produto
    ).filter(
        CissProdutoGrade.flaginativo == 'F',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 2
    )

    produtos_removidos = produtos.filter(
        CissProdutoPreco.dtalteracaopromovar > (dthr_inicial if dthr_inicial else dthr_hoje),
        CissProdutoPreco.valpromvarejo == 0
    )

    produtos = produtos.filter(
        CissProdutoPreco.dtfimpromocaovar > dt_hoje
    )

    if dthr_inicial:
        produtos = produtos.filter(
            CissProdutoPreco.dtalteracaopromovar > dthr_inicial
        )

    produtos = produtos.order_by(
        CissProdutoGrade.descrresproduto
    )
    produtos = produtos.union(produtos_removidos).all()

    return produtos[:5]


def verificaCategoriasProdutos():
    """
        Busca os produtos marcados para envio no ERP
    """
    categorias_produtos = MagCategoriaProduto.query
    categorias_produtos = categorias_produtos.count()
    if categorias_produtos:
        return True
    return False


def buscar_data_estoque_produtos():
    """
        Busca as datas de estoque de produtos
    """
    config = ConfigMagento.by_id(1)
    dtsincr = config.dtsincr_estoque if config else None

    produtos = CissProdutoGrade.query.join(
        CissProdutoEstoque.produto
    ).filter(
        CissProdutoGrade.flaginativo == 'F',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 2
    )
    if dtsincr:
        produtos = produtos.filter(
            CissProdutoEstoque.dtalteracao > dtsincr
        )
    produtos = produtos.all()[:5]

    return produtos


def converte_produtos_estoque(produtos):
    """
        Converte os produtos para atualizar o saldo de estoque
        no site
    """
    result = []

    for p in produtos:
        saldo = Stock()
        saldo.qty = p.saldo.qtdatualestoque

        mag_product = Product(validate_requireds=False)
        mag_product.sku = p.idsubproduto
        mag_product.stock_data = saldo

        result.append({
            'sku': str(p.idsubproduto),
            'data': mag_product.to_soap()
        })

    return result


def converteProduto(item, categorias):
    """
        recebe um produto e suas categorias
        e o converte para Magento Object para ser
        enviado para o site
    """

    stock = Stock()
    stock.qty = item.saldo.qtdatualestoque
    stock.is_in_stock = 1 if stock.qty else 0

    if item.valmultivendas != 1:
        stock.enable_qty_increments = 1
        stock.qty_increments = f'{item.valmultivendas:.2f}'

    attr = Attribute()
    attr.marca = item.produto.fabricante
    attr.codigo_ciss = item.idsubproduto
    attr.multiplicador = '{0:.2f}'.format(float(item.valmultivendas))
    attr.embalagem = str(item.produto.embalagem.descrembalagem)

    nome_produto = '{0} {1} - {2}'.format(
        item.produto.descrcomproduto, 
        item.subdescricao,
        item.produto.fabricante
    )        
    nome_produto = nome_produto.title()
    
    product = Product()
    product.sku = item.idsubproduto
    product.name = nome_produto
    product.description = nome_produto
    product.short_description = nome_produto
    product.price = item.preco.valprecovarejo
    product.weight = item.pesoliquido
    product.status = '1'
    product.visibility = '4'
    product.tax_class_id = '0'
    product.stock_data = stock
    product.categories = categorias
    product.additional_attributes = attr

    dt_cadastro = item.dtcadastro
    dt_novo = date.today() + timedelta(-45)

    if dt_cadastro >= dt_novo:
        from_date = str(dt_cadastro)
        to_date = str(dt_cadastro + timedelta(45))
        product.news_from_date = from_date
        product.news_to_date = to_date

    imagens = read_images()
    image = os.getcwd() + '/uploads/photos/sem_imagem.jpg'
    if product.sku in imagens:
        image = imagens[product.sku] 
    
    return {
        'sku': str(item.idsubproduto),
        'data': product.to_soap(),
        'image': image
    }


def converteProdutos(produtos):
    """
        recebe um lista dos produtos e categorias 
        e a converte para Magento Object para ser
        enviado para o site
    """
    result = {
        'produtos': [],
        'erros': []
    }
    
    for p in produtos:
        categoria_produto = MagCategoriaProduto.query
        categoria_produto = categoria_produto.filter_by(sku=p.idsubproduto)
        categoria_produto = categoria_produto.first()

        if not categoria_produto:
            result['erros'].append([
                p.idsubproduto,
                'Produto sem categoria cadastrada'
            ])
            continue

        stock = Stock()
        stock.qty = p.saldo[0].qtdatualestoque
        stock.is_in_stock = 1

        attr = Attribute()
        attr.marca = p.produto.fabricante
        attr.codigo_ciss = p.idsubproduto
        attr.multiplicador = '{0:.2f}'.format(float(p.valmultivendas))
        attr.embalagem = str(p.produto.embalagem.descrembalagem)

        nome_produto = '{0} {1} - {2}'.format(
            p.produto.descrcomproduto, 
            p.subdescricao,
            p.produto.fabricante
        )        
        nome_produto = nome_produto.title()
        
        product = Product()
        product.sku = p.idsubproduto
        product.name = nome_produto
        product.description = nome_produto
        product.short_description = nome_produto
        product.price = p.preco[0].valprecovarejo
        product.weight = 1.23
        product.status = 1
        product.visibility = 1
        product.tax_class_id = 0
        product.stock_data = stock
        product.categories = [
            categoria_produto.secao,
            categoria_produto.grupo,
            categoria_produto.subgrupo
        ]
        product.additional_attributes = attr

        dt_cadastro = p.dtcadastro
        dt_novo = date.today() + timedelta(-45)

        if dt_cadastro >= dt_novo:
            from_date = str(dt_cadastro)
            to_date = str(dt_cadastro + timedelta(45))
            product.news_from_date = from_date
            product.news_to_date = to_date

        imagens = read_images()
        image = os.getcwd() + '/uploads/photos/sem_imagem.jpg'
        if product.sku in imagens:
            image = imagens[product.sku] 

        result['produtos'].append({
            'sku': str(p.idsubproduto),
            'produto': p,
            'data': product.to_soap(),
            'image': image
        })
    
    return result


def converte_precos_produtos(produto):
    """
        Coverte o produto para atualizar o preço no site
    """

    result = {}

    if produto:
        mag_product = Product(validate_requireds=False)
        mag_product.sku = produto.idsubproduto
        mag_product.price = produto.valprecovarejo

        result = {
            'sku': str(produto.idsubproduto),
            'data': mag_product.to_soap()
        }
    
    return result


def converte_produtos_promocao(produtos):
    """
        Coverte os produtos em promoção recuperados da 
        base de dados do ERP em magento object para enviar
        para o site
    """

    result = []

    for p in produtos:
        dt_inicio = p.preco.dtinipromocaovar if p.preco.dtinipromocaovar else ''
        dt_fim = p.preco.dtfimpromocaovar if p.preco.dtfimpromocaovar else ''

        mag_product = Product(validate_requireds=False)
        mag_product.sku = p.idsubproduto
        mag_product.special_from_date = dt_inicio
        mag_product.special_to_date = dt_fim
        mag_product.special_price = p.preco.valpromvarejo

        result.append({
            'sku': str(p.idsubproduto),
            'data': mag_product.to_soap()
        })

    return result


def atualizar_base(produtos):
    """
        recebe um lista dos produtos do site e
        atualiza a base do sistema
    """
    print(produtos)
    for p in produtos:
        sku = p['sku']
        break
        
        if sku.isdigit():
            sku = int(sku)
        
        produto = CissProdutoGrade.query.filter(
            CissProdutoGrade.idsubproduto == sku,
            db.or_(
                CissProdutoGrade.idtipo != 2,
                CissProdutoGrade.idtipo != 3
            )
        ).first()

        if produto:
            produto.idmodelo = 4
            produto.idtipo = 2
            produto.update()
        
        '''    
        produto = MagProduto.by_id(sku)
        if not produto:
            produto = MagProduto()

            produto.sku = sku
            produto.inativo = False
            produto.atualiza_imagem = False

            db.session.add(produto)
        db.session.commit()
        '''
        
