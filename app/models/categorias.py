from app.application import db
from datetime import datetime


class MagCategorias(db.Model):
    """
    representa as categorias do magento
    sendo a seção a categoria primaria
    o grupo a categoria secundária e o
    subgrupo a terciaria.
    """
    __tablename__ = 'mag_categorias'

    category_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.String(60))
    name = db.Column(db.String(60))
    position = db.Column(db.Integer)
    level = db.Column(db.Integer)
    create_at = db.Column(db.DateTime(), default=datetime.now)
    update_at = db.Column(db.DateTime(), onupdate=datetime.now)

    '''
    parent = db.relationship(
        'MagCategorias',
        backref='childrens',
        remote_side=[category_id]
    )
    '''