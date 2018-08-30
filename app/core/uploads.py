from flask_uploads import UploadSet, IMAGES
from flask_uploads import UploadNotAllowed
from app.core.image_generator import cortar_image
import os


imageSet = UploadSet('photos', IMAGES)
planilhaSet = UploadSet('planilhas', ('csv',))


class Result(object):
    """
        classe base para registrar status e mensagem
        de um try catch
    """
    def __init__(self, status=True, message=''):
        self.status = status
        self.message = message
        self.url = ''


def enviar_imagem(imagem):
    """
        recebe uma imagem e salva na pasta Uploads
    """
    base_path = os.getcwd() + '/uploads/photos/'
    result = Result()

    try:
        image = imageSet.save(imagem)
        result.url = imageSet.url(image)
        image = base_path + image
        cortar_image(image, size=250, quality=90)

    except UploadNotAllowed:
        result.status = False
        result.message = 'Somente Arquivos de Imagens são aceitas.'    
    except Exception as e:
        result.status = False
        result.message = str(e)

    return result


def enviar_planilha():
    """
        recebe um CSV e salva na pasta Uploads
    """
