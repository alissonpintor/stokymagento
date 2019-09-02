# -*- coding: utf-8 -*-
from datetime import date, datetime
from app import db

# import das models
from app.models.config import ConfigMagento
from app.models.categorias import MagCategorias
from app.models.produtos import MagCategoriaProduto
from app.models.produtos import CissProdutoGrade, MagProduto
from app.models.produtos import CissProdutoEstoque, CissProdutoPreco

# import da api magento
from app.core.api_magento.product import productInfo

# import do log
from app.log import Log


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

    produtos_inativos = CissProdutoGrade.query.filter(
        CissProdutoGrade.flaginativo == 'T',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 2
    ).order_by(
        CissProdutoGrade.descrresproduto
    )

    produtos_reativados = CissProdutoGrade.query.filter(
        CissProdutoGrade.flaginativo == 'F',
        CissProdutoGrade.idmodelo == 4,
        CissProdutoGrade.idtipo == 3
    ).order_by(
        CissProdutoGrade.descrresproduto
    )

    produtos_inativos = produtos_inativos.union(produtos_reativados)
    produtos_inativos = produtos_inativos.all()

    return produtos_inativos


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

    return produtos


def buscar_imagens_alteradas():
    """
        Busca os produtos que estao no site e tiveram as imagens alteradas
    """

    produtos = MagProduto.query.filter(
        MagProduto.atualiza_imagem == True
    ).all()

    if produtos:
        skus = [p.sku for p in produtos]
        produtos = buscarProdutos(codigo=skus).filter(
            CissProdutoGrade.idtipo == 2
        ).all()

    return produtos


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

    Log.info('[ATUALIZA BASE] Iniciando a atualização da base')
    for p in produtos:
        sku = p['sku']

        if sku.isdigit():
            sku = int(sku)

        mag_produto = MagProduto.by(sku=sku)
        produto_ciss = CissProdutoGrade.by(idsubproduto=sku)
        
        if not mag_produto and produto_ciss:
            Log.info(f'[ATUALIZA BASE] Registrando o item {sku}')

            try:
                produto_site = productInfo(sku)
            except Exception:
                continue

            mag_produto = MagProduto()
            mag_produto.sku = sku
            mag_produto.idsecao = produto_site['categories'][0]
            mag_produto.idgrupo = produto_site['categories'][1]
            mag_produto.idsubgrupo = produto_site['categories'][2]
            mag_produto.atualiza_imagem = False
            mag_produto.possui_imagem = True
            
            mag_produto.update()
            Log.info('[ATUALIZA BASE]------ Registrado no Integrador')

            # salva no erp verificando se esta ativo no site
            status = produto_site['status']
            produto_ciss.idmodelo = 4
            produto_ciss.idtipo = 2 if status == '1' else 3
            produto_ciss.update()
            Log.info('[ATUALIZA BASE]------ Registrado no ERP')
    
    Log.info('[ATUALIZA BASE] Atualização da base Finalizada')

