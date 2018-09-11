# -*- coding: utf-8 -*-
from datetime import date, datetime
from app import db

# import das models
from app.models.config import ConfigMagento
from app.models.categorias import MagCategorias
from app.models.produtos import MagCategoriaProduto
from app.models.produtos import CissProdutoGrade
from app.models.produtos import CissProdutoEstoque, CissProdutoPreco


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


def buscar_categorias_produtos(id=None):
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
    produtos = produtos.all()

    return produtos


def buscar_produtos_enviados_ativos():
    """
        Busca os produtos que estao no site e inativos no ERP
    """

    produto = buscarProdutos()
    produto = produto.filter(CissProdutoGrade.idtipo == 2)
    produto = produto.order_by(CissProdutoGrade.descrresproduto)
    produto = produto.all()

    return produto


def buscar_estoque_produtos(dthr_sincr=None):
    """
        Busca as datas de estoque de produtos
    """

    produtos = CissProdutoGrade.query.join(
        CissProdutoEstoque.produto
    ).filter(
        CissProdutoGrade.flaginativo == 'F',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 2
    )
    if dthr_sincr and isinstance(dthr_sincr, datetime):
        produtos = produtos.filter(
            CissProdutoEstoque.dtalteracao > dthr_sincr
        )
    produtos = produtos.all()

    return produtos


def buscar_precos_produtos(dthr_sincr=None):
    """
        Busca os produtos para atualizar os preços no site

        Retorna uma lista com os produtos que teram os preços atualizados
        no site a partir da datahora da ultima atualização. Se a datahora
        não for informada retorna todos os produtos ativos.

        Params
        ----------
        dthr_sincr (datetime, optional)
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

    if dthr_sincr and isinstance(dthr_sincr, datetime):
        produtos = produtos.filter(
            CissProdutoPreco.dtalteracaovar > dthr_sincr)

    produtos = produtos.all()

    return produtos


def buscar_produtos_promocao(dthr_sincr=None):
    """
        Busca os produtos que estão em promocao no ERP

        Retorna uma lista com os produtos que estão na promoção a 
        partir da datahora da ultima atualização. Se a datahora
        não for informada retorna todos os produtos ativos.

        Params
        ----------
        dthr_sincr (datetime, optional)
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
        CissProdutoPreco.dtalteracaopromovar > (dthr_sincr if dthr_sincr else dthr_hoje),
        CissProdutoPreco.valpromvarejo == 0
    )

    produtos = produtos.filter(
        CissProdutoPreco.dtfimpromocaovar > dt_hoje
    )

    if dthr_sincr and isinstance(dthr_sincr, datetime):
        produtos = produtos.filter(
            CissProdutoPreco.dtalteracaopromovar > dthr_sincr
        )

    produtos = produtos.order_by(
        CissProdutoGrade.descrresproduto
    )
    produtos = produtos.union(produtos_removidos).all()

    return produtos[:15]


def verificaCategoriasProdutos():
    """
        Busca os produtos marcados para envio no ERP
    """
    categorias_produtos = MagCategoriaProduto.query
    categorias_produtos = categorias_produtos.count()
    if categorias_produtos:
        return True
    return False


def atualizar_base(produtos):
    """
        recebe um lista dos produtos do site e
        atualiza a base do sistema
    """
    
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
