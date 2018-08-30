import os
from flask import config
from flask import flash


def allowedFiles(fileName):
    """ Congigura as extensoes permitidas de upload """
    return '.' in fileName and fileName.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']


def success(message):
    """ Grava uma mensagem de sucesso para o Usuario usando o flash """
    content = {'type': 'success', 'content': message}                
    flash(content)


def info(message):
    """ Grava uma mensagem de informação para o Usuario usando o flash """
    content = {'type': 'info', 'content': message}                
    flash(content)


def warning(message):
    """ Grava uma mensagem de aviso para o Usuario usando o flash """
    content = {'type': 'warning', 'content': message}                
    flash(content)


def error(message):
    """ Grava uma mensagem de erro para o Usuario usando o flash """
    content = {'type': 'error', 'content': message}            
    flash(content)


def get_module(module):
    """ importa e retorna um modulo a partir de um path informado """
    from importlib import import_module

    if not isinstance(module, str):
        return None
    module = import_module(module)

    return module


def get_function(path):
    """ retorna uma função a partir de um path informado """
    if not isinstance(path, str):
        return None
    
    module, func = path.rsplit('.', 1)
    module = get_module(module)
    
    func = getattr(module, func)
    
    return func


def load_csv_from_bytes(filebytes):
    """ retorna csv a partir de um byte em utf-8"""
    from io import StringIO
    from csv import reader

    my_file = StringIO(filebytes.decode('utf-8'))
    csv_file = reader(my_file)

    return csv_file

base_path = os.getcwd() + '/uploads/photos'

def read_images(path=base_path, produtos=None, filtro=None):
    """ retorna csv a partir de um byte em utf-8 """
    imageExtensions = ['.jpg', '.jpeg', '.png', '.gif']
    isdir = os.path.isdir(path)
    if produtos is None:
        produtos = {}

    if isdir:
        for file in os.listdir(path):
            read_images('%s/%s' % (path, file), produtos=produtos, filtro=filtro)
    else:
        filePath = path
        extension = os.path.splitext(path)[1]

        if extension.lower() in imageExtensions:
            idProduto = os.path.splitext(path)[0]
            idProduto = idProduto.split('/')[-1]
            
            if filtro:
                idProduto = filtro(idProduto)
            
            if idProduto.isdigit():
                produtos[int(idProduto)] = filePath
    return produtos