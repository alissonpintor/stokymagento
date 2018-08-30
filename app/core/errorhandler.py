# Imports do Flask
from flask import render_template, request

def createErrorHandler(app):
    # Views para tratar os erros
    @app.errorhandler(404)
    def pageNotFound(error):
        return render_template('error-pages/error404.html'), 404


def createErrorHandler(app):
    # Views para tratar os erros
    @app.errorhandler(401)
    def pageNotFound(error):
        return render_template('error-pages/error401.html'), 401


    # View para erros internos da aplicação
    @app.errorhandler(500)
    def internalServerError(error):
        error = {
            'message': error,
            'class': error.__class__.__name__,
            'endpoint': request.endpoint
        }
        return render_template('error-pages/error500.html', error=error), 500
