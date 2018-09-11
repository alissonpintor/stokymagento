from app import assets, db, loginManager, imageSet, csvSet
from app.bundles import css, js
from app.config import app_config

from flask import Flask, send_from_directory, request, render_template, current_app
from flask import request_finished, redirect, url_for, make_response, g
from flask_login import current_user
from flask_migrate import Migrate
from flask_uploads import configure_uploads
from flask_babel import Babel
from flask_restful import Api

from app.core.celery_app import make_celery


# def create_app():

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config['dev'])
app.config.from_pyfile('config.py')

with app.app_context():
    current_app.atualiza_precos_task = None
    current_app.atualiza_promocoes_task = None
    current_app.inativar_task = None
    current_app.atualiza_estoque_task = None
    current_app.enviar_novos_task = None

# incia a flask-restful API
api = Api(app)

# importa e registras os resources
from app.api.categoria import Categoria, CategoriaList

api.add_resource(Categoria, '/api/categoria', '/api/categoria/<int:id>')
api.add_resource(CategoriaList, '/api/categorias')

# cria os assets usados
assets.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

assets.register('css', css)
assets.register('js', js)

# Incia o Celery
mycelery = make_celery(app)
from app.core import tasks

# Inicia o Login Manager
loginManager.init_app(app)

# imports do core
from app.core.errorhandler import createErrorHandler
createErrorHandler(app)

# Importa as Blueprints
from app.views.index import bp
from app.views.account.views import account
from app.views.configuration.views import configuration
from app.views.dashboard.views import dashboard
from app.views.produtos import produtos
from app.views.categorias import categorias

# Registra as Blueprints
app.register_blueprint(bp, url_prefix='/')
app.register_blueprint(account, url_prefix='/account')
app.register_blueprint(configuration, url_prefix='/configuration')
app.register_blueprint(dashboard, url_prefix='/dashboard')
app.register_blueprint(categorias, url_prefix='/categorias')
app.register_blueprint(produtos, url_prefix='/produtos')

# Import e Registro dos Custom Filters do Jinja
from app.core.filters import regitry_filters
regitry_filters(app)

# Importa as Models
from app.models import access, config, tasks
from app.models import produtos

# Correção do erro de Conexão Perdida do SQLAlchemy
from app.core.sqlalchemyerror import sqlalchemyErrorHandler

with app.app_context():
    # Cria o Banco de Dados
    db.create_all(bind=None)
    sqlalchemyErrorHandler(db)
    
    # Cria o usuario admin se não existe
    if not access.User.hasAdmin():
        access.User.createAdmin()
        access.User.createValdecir()
    
    # Cria configuração inicial do App
    if not config.Config.hasCreated():
        config.Config.createConfig()
    else:
        if (not app.config['UPLOADS_DEFAULT_URL'] 
                and config.Config.hasBaseUrl()):
            
            import os
            uploadURL = os.path.join(config.Config.hasBaseUrl(), 
                                    'uploads')
            app.config['UPLOADS_DEFAULT_URL'] = uploadURL

    from app.core.api_magento import Api
    
    config = config.ConfigMagento.query.first()

    if config:
        Api.url = config.api_url
        Api.user = config.api_user
        Api.passwd = config.api_pass
        Api.magento_version = config.magento_version


@app.before_request
def verificar_parametros_magento():
    # Verifica se os parametros do Magento Existem e caso
    # negativo o usuario é redirecionado para a tela de
    # configurações do magento
    from app.models.config import ConfigMagento
    from app.core.utils import warning
    from app.views.configuration.views import magento

    allowed_paths = [
        '/logout',
    ]

    params_magento = ConfigMagento.query.filter_by(id=1).first()
    user_is_logged = current_user.is_authenticated
    path = request.path
    
    if user_is_logged and not params_magento and path not in allowed_paths:
        warning('Os Parametros do Magento devem ser configurados')
        return make_response(magento())


# Configura o Flask-Uploads para upload de arquivos e fotos
configure_uploads(app, (imageSet, csvSet))


@app.route('/uploads/<path>/<filename>')
def uploaded_file(path, filename):
    import os
    folder = os.path.join(app.config['UPLOAD_FOLDER'], path)
    return send_from_directory(folder, filename)


# Configura o Babel para traduções
babel = Babel(app)
@babel.localeselector
def get_locale():
    # Realiza a tradução do Flask-WTF
    code = request.args.get('lang', 'pt')
    return code


@app.before_request
def verificar_tasks():
    """
        Verifica se existe alguma task e se ela esta em execução
    """

    task = current_app.atualiza_precos_task
    if task and task.state in ('FAILURE'):
        current_app.atualiza_precos_task = None

    task = current_app.atualiza_promocoes_task
    if task and task.state in ('FAILURE'):
        current_app.atualiza_promocoes_task = None
