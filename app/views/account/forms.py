from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SelectField, SubmitField
from wtforms import PasswordField, HiddenField, FileField
from wtforms.validators import DataRequired, EqualTo
from app.core.forms import widgets as w


class UpdateUserForm(FlaskForm):
    """
    Formulario para alteração dos dados do Usuário
    """

    userId = HiddenField('ID', default=0)
    userName = StringField('Nome', validators=[DataRequired()], widget=w.GeInputWidget())
    userLastName = StringField('Sobrenome', validators=[DataRequired()], widget=w.GeInputWidget())
    userEmail = StringField('Email', validators=[DataRequired()], widget=w.GeInputWidget())
    
    genderChoices = [('M', 'Masculino'), ('F', 'Feminino')]
    userGender = SelectField('Sexo', choices=genderChoices, default='M', widget=w.GeSelectWidget())
    userImage = FileField('Imagem', widget=w.GeFileWidget())

    submit = SubmitField('Atualizar')


class UpdatePasswordForm(FlaskForm):
    """
    Formulario para alteração dos dados do Usuário
    """

    userId = HiddenField('ID', default=0)
    currentPassWord = PasswordField('Senha Atual', validators=[DataRequired()], widget=w.GePasswordWidget())
    newPassWord = PasswordField('Nova Senha', validators=[DataRequired()], widget=w.GePasswordWidget())
    newPassWordVerify = PasswordField('Repita a Senha', validators=[DataRequired(), EqualTo('newPassWord')], widget=w.GePasswordWidget())

    submit = SubmitField('Alterar')

    class Meta:
        locales = ['pt-BR', 'pt']

