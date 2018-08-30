# import do app
from app import db
from app.application import app

# importa o Celery
from app.application import mycelery

# import das models usadas na view
from app.models.produtos import CissProdutoGrade, MagProduto

# Import da Api Magento
from app.core.api_magento.product import createProduct
from app.core.api_magento.product import updateImage

# Import dos Utils usados
from .utils import read_images


__all__ = ('task_test', 'enviar_produtos_task')


# Comando Celery -->> celery -A app.application.mycelery worker -E -B
def format_task_name(task_name):
    """
        Usado para formatar o nome das tarefas

        Recebe o nome de um tarefa e retira o - do nome e o converte
        em title case

        Params
        ---------
        task_name
            nome da tarefa para ser convertido. ex: enviar-produto

        Returns
        ---------
        formated_name
            o nome da tarefa convertido. ex: Enviar Produto
    """

    formated_name = task_name.title().split('-')
    formated_name = ' '.join(formated_name)

    return formated_name


@mycelery.task(bind=True, name='tarefa-teste')
def task_test(self):
    """
        Task para se usada como teste inicial do celery
    """

    import time
    total = 20

    for num in range(1, total+1):
        self.update_state(
            state='PROGRESS',
            meta={
                'name': format_task_name(self.name),
                'current': num,
                'total': total,
                'status': 'Enviando o produto {}'.format(num)
            }
        )
        time.sleep(1)

    return {
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.task(bind=True, name='enviar-produtos')
def enviar_produtos_task(self, produtos):
    """
        cria uma tarefa para enviar os produtos no site

        Params
        -----------
        produtos
            <dict> onde a chave é o código do produto e o valor é a lista
            com as  categorias dos produtos.

        Raises
        -----------
        Fault<sku já existe no site>
            Exceção lançada quando o produto já existe no site
    """

    # import do data da view de produtos
    from app.views.produtos.data import converteProduto

    total = len(produtos)
    imagens = read_images().keys()
    skus = produtos.keys()  # pega somente os ids dos produtos
    count = 1

    for sku, categorias in produtos.items():
        self.update_state(
            state='PROGRESS',
            meta={
                'name': format_task_name(self.name),
                'current': count,
                'total': total,
                'status': 'Enviando o produto {}'.format(sku)
            }
        )

        with app.app_context():
            db.engine.dispose()
            produto = CissProdutoGrade.by(idsubproduto=int(sku))
            mag_produto = MagProduto.by(sku=int(sku))

            if not mag_produto:
                mag_produto = MagProduto()
                mag_produto.sku = produto.idsubproduto

            mag_produto.idsecao = categorias[0]
            mag_produto.idgrupo = categorias[1]
            mag_produto.idsubgrupo = categorias[2]

            data = converteProduto(produto, categorias)
            try:
                createProduct(
                    data['sku'],
                    'simple',
                    '4',
                    data['data']
                )
                updateImage(
                    data['image'],
                    data['sku'],
                    data['sku']
                )

                # altera o tipo do produto como enviado no erp
                produto.idtipo = 2
                produto.update()

                # salva se o produto possui imagem ou nao
                possui_imagem = True if produto.idsubproduto in imagens else False
                mag_produto.atualiza_imagem = not possui_imagem
                mag_produto.possui_imagem = possui_imagem
                mag_produto.update()

                skus.remove(sku)

            except Exception as erro:
                pass

        count += 1

    return {
        'current': total,
        'total': total,
        'status': 'complete'
    }
