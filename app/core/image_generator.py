from PIL import Image, ImageColor
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import io

Image.MAX_IMAGE_PIXELS = None


def alpha_to_color(image, color=(255, 255, 255)):
    """Set all fully transparent pixels of an RGBA image to the specified color.
    This is a very simple solution that might leave over some ugly edges, due
    to semi-transparent areas. You should use alpha_composite_with color instead.

    Source: http://stackoverflow.com/a/9166671/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    x = np.array(image)
    r, g, b, a = np.rollaxis(x, axis=-1)
    r[a == 0] = color[0]
    g[a == 0] = color[1]
    b[a == 0] = color[2]
    x = np.dstack([r, g, b, a])
    return Image.fromarray(x, 'RGBA')


def pure_pil_alpha_to_color_v2(image, color=(255, 255, 255)):
    """Alpha composite an RGBA Image with a specified color.

    Simpler, faster version than the solutions above.

    Source: http://stackoverflow.com/a/9459208/284318

    Keyword Arguments:
    image -- PIL RGBA Image object
    color -- Tuple r, g, b (default 255, 255, 255)

    """
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, color)
    background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
    return background


def genImage(original, new, size=1500, quality=75, text=None):
    original = Image.open(original)

    if original.mode == 'RGBA':
        original = pure_pil_alpha_to_color_v2(original)
    
    original = original.convert('RGB')

    newImage = Image.new('RGB', (size, size), color=(255, 255, 255))
    Xsize, Ysize = original.size

    perc = size / Xsize if Xsize > Ysize else size / Ysize
    Xsize = round(Xsize * perc)
    Ysize = round(Ysize * perc)
    # print(Xsize, Ysize)
    original = original.resize((Xsize, Ysize))

    if text:
        boxXSize = len(text) * 11
        draw = ImageDraw.Draw(original)
        font = ImageFont.truetype("Arial.ttf", 20)
        draw.rectangle([7, 7, boxXSize, 37], fill=(100, 255, 255))
        draw.text((10, 10), text, (0, 0, 0), font=font)

    Xbox = 0 if (size - Xsize) is 0 else round((size - Xsize) / 2)
    Ybox = 0 if (size - Ysize) is 0 else round((size - Ysize) / 2)    
    box = (Xbox, Ybox)
    newImage.paste(original, box)

    newImage.save(new, 'JPEG', dpi=(72, 72), quality=quality)


def cortar_image(imagem, size=500, quality=75):
    """
        Cortar a imagem para ficar com altura e largura iguais
    """
    nome = imagem
    imagem = Image.open(imagem)

    if imagem.mode == 'RGBA':
        imagem = pure_pil_alpha_to_color_v2(imagem)

    imagem = imagem.convert('RGB')

    Xsize, Ysize = imagem.size
    xCoord = 0 if Xsize <= Ysize else (Xsize - Ysize)/2
    yCoord = 0 if Ysize <= Xsize else (Ysize - Xsize)/2
    cropBox = (xCoord, yCoord, Xsize-xCoord, Ysize-yCoord)

    imagem = imagem.crop(cropBox)
    imagem.load()

    resizeBox = (size, size)
    imagem = imagem.resize(resizeBox)

    imagem.save(nome, 'JPEG', dpi=(72, 72), quality=quality)
