# -*- coding: utf-8 -*-
import os
from datetime import date, timedelta

# import das models
from app.models.produtos import MagCategoriaProduto

# import da API Magento
from app.core.api_magento.objects import Stock, Product, Attribute

# import dos utils
from app.core.utils import read_images


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


def converte_precos_produtos(produtos):
    """
        Coverte o produto para atualizar o preço no site
    """

    result = []

    for p in produtos:
        mag_product = Product(validate_requireds=False)
        mag_product.sku = p.idsubproduto
        mag_product.price = p.valprecovarejo

        result.append({
            'sku': str(p.idsubproduto),
            'data': mag_product.to_soap()
        })

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
