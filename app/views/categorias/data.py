# -*- coding: utf-8 -*-

# import das models
from app.models.config import ConfigMagento
from app.models.categorias import MagCategorias

# import da API Magento
from app.core.api_magento.category import category_tree


class ErrorHandler():
    """
        Manipulador dos erros gerados ao realizar
        as ações na api do magento
    """


def buscar_categorias_site():
    """
        Busca do Site as Categorias de produtos cadastradas
    """
    def filtrar_categorias(categorias, data):

        if isinstance(categorias, list):
            for c in categorias:
                filtrar_categorias(c, data)     

        if isinstance(categorias, dict):
            categoria = {
                'category_id': categorias['category_id'],
                'parent_id': categorias['parent_id'],
                'is_active': categorias['is_active'],
                'name': categorias['name'],
                'position': categorias['position'],
                'level': categorias['level']
            }
            data.append(categoria)
            
            if categorias['children']:
                filtrar_categorias(categorias['children'], data)        
        
        return data
    
    params = ConfigMagento.by_id(1)
    
    if params:
        categorias = category_tree(parent_id=params.categoria_default)
        categorias = categorias['children']
        if not categorias:
            return None
    
    data = []
    categorias = filtrar_categorias(categorias, data)

    return categorias


def gravar_categoria(
        category_id,
        parent_id,
        is_active,
        name,
        position,
        level
    ):
    """
        Recebe os parametros e registra em mag_categorias
        as categorias existentes no site
    """
    
    categoria = MagCategorias.by_id(category_id)
    if categoria is None:
        categoria = MagCategorias()
        categoria.category_id = int(category_id)

    categoria.parent_id = int(parent_id)
    categoria.is_active = int(is_active)
    categoria.name = str(name)
    categoria.position = int(position)
    categoria.level = int(level)

    categoria.update()


def registrar_categorias():
    """
        Busca do Site as Categorias de produtos cadastradas
    """

    categorias = buscar_categorias_site()

    for c in categorias:
        gravar_categoria(**c)
