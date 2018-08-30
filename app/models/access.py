from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, loginManager
import datetime


class User(UserMixin, db.Model):
    """
    Create an User table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    userName = db.Column(db.String(60), index=True, unique=True)
    firstName = db.Column(db.String(60))
    lastName = db.Column(db.String(60))
    passwordHash = db.Column(db.String(128))
    image = db.Column(db.String(200))

    genderCheck = db.CheckConstraint("gender='M' or gender='F'")
    gender = db.Column(db.String(1), genderCheck)

    create = db.Column(db.Date, default=datetime.date.today)
    update = db.Column(db.Date, onupdate=datetime.date.today)

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.passwordHash = generate_password_hash(password)

    def verifyPassword(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.passwordHash, password)

    def __repr__(self):
        return '<Employee: {}>'.format(self.username)
    
    @classmethod
    def createAdmin(cls):
        admin = cls()
        
        admin.firstName = 'Admin'
        admin.lastName = 'System'
        admin.email = 'admin@admin.net'
        admin.userName = 'admin'
        admin.gender = 'M'
        admin.password = '123456'
        admin.userImage = None

        db.session.add(admin)
        db.session.commit()
    
    @classmethod
    def createValdecir(cls):
        admin = cls()

        admin.firstName = 'Valdecir'
        admin.lastName = 'Pintor'
        admin.email = 'valdecir@stoky.com.br'
        admin.userName = 'valdecir'
        admin.gender = 'M'
        admin.password = '999825928'
        admin.userImage = None

        db.session.add(admin)
        db.session.commit()

    @classmethod
    def hasAdmin(cls):
        exist = cls.query.filter_by(userName='admin').first()
        return True if exist else False        


# Set up user_loader
@loginManager.user_loader
def loadUser(userId):
    return User.query.get(int(userId))
