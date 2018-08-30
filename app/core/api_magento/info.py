import magento
from app.core.api_magento import Api


api = Api()


def magentoInfo():    
    with magento.Magento(api.url, api.user, api.passwd) as magento_api:
        magento_info = magento_api.info()
        return magento_info
