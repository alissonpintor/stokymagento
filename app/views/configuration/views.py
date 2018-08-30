from flask import Blueprint, render_template, current_app
from flask_login import login_required
from flask_uploads import configure_uploads
from app import db, imageSet
from app.core.api_magento import Api

# Import dos Forms da View
from app.views.configuration.forms import ConfigForm, ConfigMagentoForm

# Import das Models usadas pela View
from app.models.config import Config, ConfigMagento

# import dos utils
from app.core.utils import success


configuration = Blueprint('configuration', __name__)


@configuration.route('/', methods=['GET', 'POST'])
def index():
    config = Config.query.filter_by(id=1).first()
    form = ConfigForm()

    if config and not form.baseURL.data:
        form.configId.data = config.id
        form.baseURL.data = config.baseUrl
    
    if form.validate_on_submit():
        import os
        config.baseUrl = form.baseURL.data
        
        uploadURL = os.path.join(form.baseURL.data, 'uploads')
        current_app.config.update(
            UPLOADS_DEFAULT_URL=uploadURL
        )
        configure_uploads(current_app, (imageSet, ))

        db.session.add(config)
        db.session.commit()

    content = {
        'title': 'Configurações do Sistema',
        'form': form
    }
    return render_template('configurations/main.html', **content)


@configuration.route('/magento', methods=['GET', 'POST'])
def magento():
    config = ConfigMagento.query.filter_by(id=1).first()
    if not config:
        config = ConfigMagento()
    
    form = ConfigMagentoForm()

    if config and config.id and not form.config_id.data:
        form.config_id.data = config.id
        form.api_url.data = config.api_url
        form.api_user.data = config.api_user
        form.api_pass.data = config.api_pass
        form.magento_version.data = config.magento_version
        form.categoria_default.data = config.categoria_default
        form.dtsincr_estoque.data = config.estoque_dtsincr

    if form.validate_on_submit():
        config.api_url = form.api_url.data
        config.api_user = form.api_user.data
        config.api_pass = form.api_pass.data
        config.magento_version = form.magento_version.data
        config.categoria_default = form.categoria_default.data

        api = Api()
        api.url = form.api_url.data
        api.user = form.api_user.data
        api.passwd = form.api_pass.data
        api.magento_version = form.magento_version.data

        db.session.add(config)
        db.session.commit()

        success('Configurações atualizadas com sucesso.')

    content = {
        'title': 'Configurações do Magento',
        'form': form
    }
    return render_template('configurations/magento.html', **content)
