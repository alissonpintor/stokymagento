from app.application import db
from datetime import date


class MagTasks(db.Model):
    """
    representa as categorias do magento
    sendo a seção a categoria primaria
    o grupo a categoria secundária e o
    subgrupo a terciaria.
    """
    __tablename__ = 'mag_tasks'

    task_id = db.Column(db.String(100), primary_key=True)
    task_name = db.Column(db.String(60))
    create_at = db.Column(db.Date(), default=date.today)
    update_at = db.Column(db.Date(), onupdate=date.today)
    is_active = db.Column(
        db.String(1),
        db.CheckConstraint("is_active='T' or is_active='F'")
    )

    @classmethod
    def get_active_tasks(cls):
        return db.session.query(
            cls
        ).filter(
            cls.is_active == 'T'
        ).all()


class MagTasksQueue(db.Model):
    """
    representa as tasks que foram 
    enviadas para o celery para
    serem executadas
    """
    __tablename__ = 'mag_tasks_queue'

    task_id = db.Column(db.String(60), primary_key=True)