from app.models.config import ConfigMagento
from flask import current_app


class Api(object):
    _instance = None
    _attrs = ['url', 'user', 'passwd', 'magento_version']
    
    url = None
    user = None
    passwd = None
    magento_version = None

    def __new__(cls, *args, **kwargs):        
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __setattr__(self, attr, value):
        if attr not in self._attrs:
            error = "Valor de atributo '%s' inválido para a Api()" % attr
            raise Exception(error)
        
        super().__setattr__(attr, value)
