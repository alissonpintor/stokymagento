import magento
from app.core.api_magento import Api


api = Api()

def category_tree(parent_id=None):
    """
    Lista a arvore de categorias
    """
    with magento.Category(api.url, api.user, api.passwd) as category:
        categorys = category.tree(
            parent_id=parent_id
        )
        return categorys
