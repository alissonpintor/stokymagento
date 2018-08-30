from app import db


class Config(db.Model):
    """
    Create an Config App table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'config'

    id = db.Column(db.Integer, primary_key=True)
    baseUrl = db.Column(db.String(200))

    @classmethod
    def hasCreated(cls):
        exist = cls.query.filter_by(id=1).first()
        return True if exist else False
    
    @classmethod
    def createConfig(cls):
        config = cls()
        config.baseUrl = None

        db.session.add(config)
        db.session.commit()
    
    @classmethod
    def hasBaseUrl(cls):
        config = cls.query.filter_by(id=1).first()
        return config.baseUrl


class ConfigMagento(db.Model):
    """
        Model que possui os parametros de configuracao
        de acesso da api do Magento
    """

    __tablename__ = 'mag_config'

    id = db.Column(db.Integer, primary_key=True)
    api_url = db.Column(db.String(200), nullable=False)
    api_user = db.Column(db.String(30), nullable=False)
    api_pass = db.Column(db.String(30), nullable=False)
    magento_version = db.Column(db.String(10), nullable=False)
    categoria_default = db.Column(db.Integer, nullable=False)
    dtsincr_produto = db.Column(db.DateTime)
    dtsincr_preco = db.Column(db.DateTime)
    dtsincr_estoque = db.Column(db.DateTime)
    dtsincr_promocao = db.Column(db.DateTime)
    dtsincr_imagens = db.Column(db.DateTime)
    dtsincr_inativos = db.Column(db.DateTime)
