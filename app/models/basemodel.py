from flask_sqlalchemy import Model
from sqlalchemy import exc as core_exc


class Result(object):
    """
        Classe que recebe o resultado
    """
    def __init__(self, status, message):
        self.status = status
        self.message = message


class BaseModel(Model):
    """
        classe Model base que contem metodos comuns
        como delete, search by id, update
    """
    def update(self):
        from app import db
        
        try:
            db.session.add(self)
            db.session.commit()
            return Result(status=True, message='Registro realizado com sucesso')
        
        except Exception as e:
            return Result(status=False, message=str(e))
    
    def delete(self):
        from app import db
        
        try:
            db.session.delete(self)
            db.session.commit()
            return Result(status=True, message='Registro excluído com sucesso')
        
        except core_exc.IntegrityError:
            return Result(status=False, message='Não foi possível excluir. Erro de Integridade')
        
        except Exception as e:
            return Result(status=False, message=str(e))
    
    def json(self, get_relations=False):
        data = {}
        klass = self.__class__

        for k in klass.__table__.columns.keys():
            value = getattr(self, k)
            data[k] = str(value)
        
        if not get_relations:
            return data
        
        for k in klass.__mapper__.relationships.keys():
            values = getattr(self, k)
            
            if type(values) == InstrumentedList:
                data[k] = []
                for value in values:
                    data[k].append(value)
            else:
                data[k] = values.json()
        
        return data
    
    @classmethod
    def by_id(cls, id):
        from app import db

        primary_key = db.inspect(cls).primary_key[0]
        data = db.session.query(
            cls
        ).filter(
            primary_key==id
        ).first()
        
        return data
    
    @classmethod
    def by(cls, get_first=True, **kwargs):
        from app import db

        columns = cls.__table__.columns
        data = db.session.query(cls)

        for k, v in kwargs.items():
            if columns.has_key(k):
                column = columns[k]
                data = data.filter(column==v)
            else:
                return None
        
        data = data.first() if get_first else data.all()
        
        return data
    
    @classmethod
    def all(cls):
        from app import db

        data = cls.query.all()        
        return data