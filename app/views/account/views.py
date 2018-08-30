from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required
from app import db

# Imports dos Forms do Account View
from app.views.account.forms import UpdateUserForm, UpdatePasswordForm

# Import dos Models utilizados na View
from app.models.access import User

# Import do core
from app.core.utils import success, warning, error
from app.core.uploads import enviar_imagem


account = Blueprint('account', __name__)


@account.route('/')
@login_required
def index():
    title = 'Minha Conta'
    return render_template('account/main.html', title=title)


@account.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id=None):
    form = UpdateUserForm()
    user = User.query.filter_by(id=id).first()

    if user and form.userId.data == 0:
        form.userId.data = user.id
        form.userName.data = user.firstName
        form.userLastName.data = user.lastName
        form.userEmail.data = user.email
        form.userGender.data = user.gender

    if form.validate_on_submit():
        user.firstName = form.userName.data
        user.lastName = form.userLastName.data
        user.email = form.userEmail.data
        user.gender = form.userGender.data

        if form.userImage.data:
            if current_app.config['UPLOADS_DEFAULT_URL'] is None:
                warning('A URL Base do Sistema não está configurada para salvar a images.')
                return redirect(url_for('account.update', id=id))

            image = enviar_imagem(form.userImage.data)
            if not image.status:
                error(image.message)
                return redirect(url_for('account.update', id=id))

            user.image = image.url

        db.session.add(user)
        db.session.commit()
        success('Dados alterados com sucesso.')

        return redirect(url_for('account.index'))

    content = {
        'title': 'Minha Conta',
        'form': form
    }
    return render_template('account/update.html', **content)


@account.route('/update-password/<int:id>', methods=['GET', 'POST'])
@login_required
def updatePassword(id):
    form = UpdatePasswordForm()

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(id=id).first()

        if user and user.verifyPassword(form.currentPassWord.data):
            user.password = form.newPassWord.data
            db.session.add(user)
            db.session.commit()

            message = {'type': 'success', 'content': 'Senha alterada com sucesso.'}
            flash(message)

            return redirect(url_for('account.index'))

        else:
            message = {'type': 'danger', 'content': 'A Senha Atual está incorreta.'}
            flash(message)

    content = {
        'title': 'Minha Conta',
        'form': form
    }
    return render_template('account/update-password.html', **content)
