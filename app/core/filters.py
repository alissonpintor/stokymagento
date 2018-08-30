import datetime
import locale


def date_format(date, format='%d/%m/%Y'):
    """
        recebe uma data e a formata no padrao informado
        ou default xx/xx/xxxx
    """
    if isinstance(date, datetime.date):
        return date.strftime(format=format)


def currency(value):
    """
        recebe uma valor float e a formata no padrao de moeda
        Reais/Brasileiro
    """
    return locale.currency(value)


def regitry_filters(app):
    """
        registra todos os filtros criados
    """
    app.jinja_env.filters['date_format'] = date_format
    app.jinja_env.filters['currency'] = currency