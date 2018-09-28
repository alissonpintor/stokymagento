import magento
from app.core.api_magento import Api


api = Api()

def productInfo(sku):
    """
    Tras as informações do produto pelo sku
    """
    with magento.Product(api.url, api.user, api.passwd) as productApi:
        product = productApi.info(
            product=sku,
            identifierType='sku'
        )

        return product


def productList(filtro=None):
    """
    Tras um lista com todos os produtos do site
    e se algum filtro for passado tras a lista
    de acordo com as especificações do filtro.

    Exemplo Filtro
    ----------------
        filtro = {
            'special_to_date': {
                'gteq': '2018-07-24'
            }
        }
        produto = productList(filtro=filtro)

    """
    with magento.Product(api.url, api.user, api.passwd) as productApi:
        products = productApi.list(filters=filtro, store_view=1)
        return products


def createProduct(sku, ptype, attrSet, product):
    """
    Cadastra um novo produto no Magento
    """
    with magento.Product(api.url, api.user, api.passwd) as productApi:
        new_item = productApi.create(
            product_type=ptype,
            attribute_set_id=attrSet,
            sku=sku,
            data=product
        )

        return new_item


def updateProduct(sku, data):
    """
    Atualiza um produto existente no Magento
    """
    item = None
    with magento.Product(api.url, api.user, api.passwd) as productApi:
        item = productApi.update(
            product=sku,
            data=data,
            identifierType="sku"
        )
    return item


def updateProductList(products):
    """
    Atualiza os produtos no Site a partir de uma lista de produtos
    """
    items = []
    erros = []
    with magento.Product(api.url, api.user, api.passwd) as productApi:
        for p in products:
            try:
                item = productApi.update(
                    product=p['sku'],
                    data=p['data'],
                    identifierType="sku"
                )
                items.append(item)
            except Exception as e:
                erro = {'item': p['sku'], 'erro': str(e)}
                erros.append(erro)

    return items, erros


def updateImage(image, name, sku):
    with magento.ProductImages(api.url, api.user, api.passwd) as prodImage:
        import base64
        
        image = open(image, 'rb')
        imageEncoded = base64.b64encode(image.read())

        image64 = {
            'content': imageEncoded,
            'mime': 'image/jpeg',
            'name': name
        }

        productImage = {
            'file': image64,
            'label': 'Imagem_%s' % name,
            'position': 1,
            'types': ['image', 'thumbnail', 'small_image'],
            'exclude': '0',
            'remove': '0'
        }

        prodImage.create(
            product=sku,
            data=productImage,
            identifierType='sku'
        )


def listImage(sku):
    with magento.ProductImages(api.url, api.user, api.passwd) as prodImage:
        images = prodImage.list(
            product=sku,
            identifierType='sku'
        )
        return images


def removeImage(sku, image_name):
    with magento.ProductImages(api.url, api.user, api.passwd) as prodImage:
        prodImage.remove(
            product=sku,
            img_file_name=f'Imagem_{image_name}',
            identifierType='sku'
        )
