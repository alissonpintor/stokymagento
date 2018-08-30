from flask_assets import Environment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES
from app.models.basemodel import BaseModel

assets = Environment()
db = SQLAlchemy(model_class=BaseModel)
loginManager = LoginManager()
imageSet = UploadSet('photos', IMAGES)
csvSet = UploadSet('csv', ('csv',))
