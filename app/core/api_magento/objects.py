import copy
from datetime import date, timedelta


class BaseObject(object):
    """
    Representa o objeto Base das Entidades
    do Magento
    """
    _REQUIREDS = None
    _FIELDS = None

    def __init__(self, validate_requireds=True):
        self._VALIDATE = True if validate_requireds else False
        
        if self._REQUIREDS:
            for attr in self._REQUIREDS:
                self.__setattr__(attr, None)
        if self._FIELDS:
            for attr in self._FIELDS:
                self.__setattr__(attr, None)
    
    def __setattr__(self, name, value):
        if name is '_VALIDATE':
            super().__setattr__(name, value)
        if self._REQUIREDS or self._FIELDS:
            if name in self._REQUIREDS or name in self._FIELDS:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def _verify_requireds(self):
        if self._REQUIREDS is None or self._VALIDATE is False:
            return True
        
        for key in self._REQUIREDS:
            value = getattr(self, key)
            if value is None:
                return False
        
        return True

    def _get_data(self):
        data = {}
        for key, value in self.__dict__.items():
            if value:
                if isinstance(value, BaseObject):
                    data[key] = value._get_data()
                elif isinstance(value, list):
                    data[key] = [str(v).title() for v in value]
                elif isinstance(value, dict):
                    data[key] = {k: str(v).title() for k, v in value.items()}
                else:
                    if key is not '_VALIDATE':
                        data[key] = str(value).title()
        return data

    def to_soap(self):
        if not self._verify_requireds():
            klass = self.__class__.__name__
            raise Exception('Empty values requireds in {}'.format(klass))

        data = self._get_data()
        data.pop('sku', None)
        data.pop('_VALIDATE', None)
        
        return data
    
    def from_object(self, obj, mapper):
        for ob_key, api_key in mapper:
            if not isinstance(ob_key, tuple):
                self.__setattr__(api_key, str(obj.__getattribute__(ob_key)))
            else:
                value = None
                for i, k in enumerate(ob_key):
                    if i == 0:
                        value = obj.__getattribute__(k)
                    else:
                        value = value.__getattribute__(k)
                self.__setattr__(api_key, str(value))


class Stock(BaseObject):
    """
    Representa o obbjeto stokc dos produtos
    no magento que contem as informações de
    estoque do produto
    """
    _REQUIREDS = (
        "qty",
        "is_in_stock"
    )

    _FIELDS = (
        "manage_stock", "use_config_manage_stock",
        "min_qty", "use_config_min_qty", "min_sale_qty",
        "use_config_min_sale_qty", "max_sale_qty",
        "use_config_max_sale_qty", "is_qty_decimal",
        "backorders", "use_config_backorders",
        "notify_stock_qty", "use_config_notify_stock_qty",
        "use_config_qty_increments", "qty_increments", "enable_qty_increments",
        "use_config_enable_qty_inc"
    )        


class Attribute(BaseObject):
    """
    Representa os atributos adicionais do
    magento que contem os custom attibutes
    dos produtos do magento
    """
    def _get_data(self):
        data = super(Attribute, self)._get_data()
        data = {'single_data': data}
        return data


class Product(BaseObject):
    _REQUIREDS = (
        'sku', 'name',
        'description',
        'short_description',
        'price', 'weight',
        'status', 'visibility',
        'tax_class_id'
    )

    _FIELDS = (
        'categories', 'websites', 'url_key',
        'url_path', 'website_ids', 'has_options',
        'special_price', 'special_from_date', 'special_to_date',
        'meta_title', 'meta_keyword', 'meta_description',
        'custom_design', 'custom_layout_update',
        'options_container', 'stock_data', 'additional_attributes',
        'news_from_date', 'news_to_date'
    )

    def from_object(self, obj, mapper):
        super().from_object(obj, mapper)
        
        self.__setattr__('price', '16.00')
        self.__setattr__('weight', '2.30')
        self.__setattr__('status', '1')
        self.__setattr__('visibility', '1')
        self.__setattr__('tax_class_id', '1')


if __name__ == '__main__':
    stock = Stock()
    stock.qty = 10
    stock.is_in_stock = 1

    attr = Attribute()
    attr.marca = 'Perlex'
    attr.cod_ciss = 13504
    
    product = Product()
    product.sku = 123
    product.name = 'produto 123'
    product.description = 'produto 123'
    product.short_description = 'produto 123'
    product.price = 17.23
    product.weight = 1.23
    product.status = 1
    product.visibility = 1
    product.tax_class_id = 0
    product.stock_data = stock
    product.categories = [1,2,3]
    product.single_data = attr

    print(product.to_soap())

