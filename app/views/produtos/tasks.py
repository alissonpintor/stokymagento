from datetime import datetime

# import do app
from app import db
from app.application import app

# impor do Log
from app.log import Log

# importa o Celery
from celery.schedules import crontab
from app.application import mycelery

# import das models usadas na view
from app.models.config import ConfigMagento
from app.models.produtos import CissProdutoGrade, MagProduto

# Import da Api Magento
from xmlrpc.client import Fault
from app.core.api_magento.product import createProduct, updateProduct
from app.core.api_magento.product import updateImage, removeImage, listImage

# Import dos Utils usados
from app.core.utils import read_images

# import dos filters
from .filter import buscar_precos_produtos, buscar_produtos_promocao
from .filter import buscar_produtos_inativos, buscar_estoque_produtos

# import dos converts
from .convert import converte_precos_produtos, converte_produtos_promocao
from .convert import converte_produto_inativo, converte_produtos_estoque
from .convert import converte_produto_novo


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


@mycelery.task(bind=True, name='atualiza-imagem')
def atualiza_imagem_task(self):
    """
        Usado para atualizar as imagens de produtos que ja estão no site
    """

    with app.app_context():
        Log.info(f'[IMAGENS] Iniciando o envio dos produtos.')
        db.engine.dispose()

        produtos = MagProduto.query.filter(
            MagProduto.atualiza_imagem == True
        ).all()

        imagens = read_images()
        concluidos = 0
        erros_count = 0
        erros = []
        count = 0
        total = len(produtos)

        for p in produtos:
            Log.info(f'[IMAGENS] Iniciando o envio do item {p.sku}.')

            self.update_state(
                state='PROGRESS',
                meta={
                    'name': format_task_name(self.name),
                    'complete': concluidos,
                    'errors_count': erros_count,
                    'errors': erros,
                    'current': count,
                    'total': total,
                    'status': f'Enviando o produto {p.sku}'
                }
            )

            try:
                imagem = imagens.get(p.sku, None)
                nome_imagem = str(p.sku)
                
                if not imagem:
                    Log.info(f'[IMAGENS]------ Produto sem imagem')
                    count += 1
                    continue

                imagens_site = listImage(
                    p.sku
                )

                # verifca se o produto possui imagens para serem excluidas
                # antes de enviar a nova
                if imagens_site:
                    for im in imagens_site:
                        # se ao tentar excluir a imagem gerar a exceção de que
                        # a imagem nao existe na galeria do produto salva como
                        # erro para ser exida ao usuario
                        try:
                            removeImage(
                                p.sku,
                                im['file'],
                            )                        
                        except Fault as e:
                            pass

                    # se existir imagens altera o nome para adcionar um contador
                    # exemplo: 13504_6
                    nome_imagem = f'{nome_imagem}_{len(imagens_site) + 1}'

                updateImage(
                    imagem,
                    nome_imagem,
                    str(p.sku)
                )
                Log.info(f'[IMAGENS]------ Imagem enviada com sucesso')

                p.atualiza_imagem = False
                p.update()
                Log.info(f'[IMAGENS]------ Produto Atulizado no Integrador')

                concluidos += 1

            except Exception as e:
                erros_count += 1
                erros.append(f'Produto: {p.sku} -------- Erro: {e}')

                Log.error(
                    f'[IMAGENS] Erro ao enviar o produto {p.sku} erro: {e}')

            count += 1

        Log.info(f'[IMAGENS] Envio de produtos finalizado.')

        return {
            'name': format_task_name(self.name),
            'complete': concluidos,
            'errors_count': erros_count,
            'errors': erros,
            'current': total,
            'total': total,
            'status': 'complete'
        }


@mycelery.task(bind=True, name='enviar-produtos')
def enviar_novos_task(self, produtos):
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

    Log.info(f'[NOVOS] Iniciando o envio dos produtos.')

    imagens = read_images().keys()
    concluidos = 0
    erros_count = 0
    erros = []
    count = 0
    total = len(produtos)

    with app.app_context():
        db.engine.dispose()
 
        for sku, categorias in produtos.items():
            self.update_state(
                state='PROGRESS',
                meta={
                    'name': format_task_name(self.name),
                    'complete': concluidos,
                    'errors_count': erros_count,
                    'errors': erros,
                    'current': count,
                    'total': total,
                    'status': f'Enviando o produto {sku}'
                }
            )

            try:
                Log.info(f'[NOVOS] Iniciando o envio do item {sku}.')
                produto_erp = CissProdutoGrade.by(idsubproduto=int(sku))

                mag_produto = MagProduto.by(sku=int(sku))
                if not mag_produto:
                    mag_produto = MagProduto()
                    mag_produto.sku = produto_erp.idsubproduto

                mag_produto.idsecao = categorias[0]
                mag_produto.idgrupo = categorias[1]
                mag_produto.idsubgrupo = categorias[2]

                produto = converte_produto_novo(produto_erp, categorias)

                createProduct(
                    produto['sku'],
                    'simple',
                    '4',
                    produto['data']
                )
                updateImage(
                    produto['image'],
                    produto['sku'],
                    produto['sku']
                )
                Log.info(f'[NOVOS]------ Enviado para o site')

                # altera o tipo do produto como enviado no erp
                produto_erp.idtipo = 2
                produto_erp.update()

                # salva se o produto possui imagem ou nao
                possui_imagem = True if sku in imagens else False
                mag_produto.atualiza_imagem = False
                mag_produto.possui_imagem = possui_imagem
                mag_produto.update()

                Log.info(f'[NOVOS]------ Gravado no ERP e Integrador')

                concluidos += 1
            
            except Fault as fault:
                if fault.faultCode == 1:
                    produto_erp.idtipo = 2
                    produto_erp.update()
                
                erros_count += 1
                erros.append(f'Produto: {sku} -------- Erro: {fault}')

                Log.error(
                    f'[NOVOS] Erro ao enviar o produto {sku} erro: {fault}')

            except Exception as e:
                erros_count += 1
                erros.append(f'Produto: {sku} -------- Erro: {e}')

                Log.error(
                    f'[NOVOS] Erro ao enviar o produto {sku} erro: {e}')

            count += 1

            self.update_state(
                state='PROGRESS',
                meta={
                    'name': format_task_name(self.name),
                    'complete': concluidos,
                    'errors_count': erros_count,
                    'errors': erros,
                    'current': count,
                    'total': total,
                    'status': f'Enviando o produto {sku}'
                }
            )

        Log.info(f'[NOVOS] Envio de produtos finalizado.')

    return {
        'name': format_task_name(self.name),
        'complete': concluidos,
        'errors_count': erros_count,
        'errors': erros,
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.task(bind=True, name='atualizar-estoque')
def atualiza_estoque_task(self):
    """
        cria uma tarefa para atualizar os estoques dos produtos no site

        Raises
        -----------
        Fault<sku já existe no site>
            Exceção lançada quando o produto já existe no site
    """

    Log.info(f'[ESTOQUE] Iniciando o envio dos produtos.')
    config = ConfigMagento.by_id(1)
    dthr_sincr = datetime.now()
    produtos = buscar_estoque_produtos(dthr_sincr=config.dtsincr_estoque)
    produtos = converte_produtos_estoque(produtos)

    concluidos = 0
    erros_count = 0
    erros = []
    count = 0
    total = len(produtos)

    for p in produtos:
        self.update_state(
            state='PROGRESS',
            meta={
                'name': format_task_name(self.name),
                'complete': concluidos,
                'errors_count': erros_count,
                'errors': erros,
                'current': count,
                'total': total,
                'status': f'Enviando o produto {p["sku"]}'
            }
        )

        try:
            Log.info(f'[ESTOQUE] Iniciando o envio do item {p["sku"]}.')
            updateProduct(
                sku=p['sku'],
                data=p['data']
            )
            Log.info(f'[ESTOQUE]------ Enviado para o site')

            concluidos += 1

        except Exception as e:
            erros_count += 1
            erros.append(f'Produto: {p["sku"]} -------- Erro: {e}')

            Log.error(
                f'[ESTOQUE] Erro ao enviar o produto {p["sku"]} erro: {e}')

        count += 1

    Log.info(f'[ESTOQUE] Envio de produtos finalizado.')

    with app.app_context():
        db.engine.dispose()  # corrigi o erro do postgres
        config.dtsincr_estoque = dthr_sincr
        config.update()

    return {
        'name': format_task_name(self.name),
        'complete': concluidos,
        'errors_count': erros_count,
        'errors': erros,
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.task(bind=True, name='atualizar-preco')
def atualiza_precos_task(self):
    """
        cria uma tarefa para atualizar os preços dos produtos no site

        Params
        -----------
        produtos (list)
            lista de skus do produtos que serão atualizados

        Raises
        -----------
        Fault<sku já existe no site>
            Exceção lançada quando o produto já existe no site
    """

    Log.info(f'[PREÇO] Iniciando o envio dos produtos.')
    config = ConfigMagento.by_id(1)
    dthr_sincr = datetime.now()
    produtos = buscar_precos_produtos(dthr_sincr=config.dtsincr_preco)    
    produtos = converte_precos_produtos(produtos)

    concluidos = 0
    erros_count = 0
    erros = []
    count = 0
    total = len(produtos)

    for p in produtos:
        self.update_state(
            state='PROGRESS',
            meta={
                'name': format_task_name(self.name),
                'complete': concluidos,
                'errors_count': erros_count,
                'errors': erros,
                'current': count,
                'total': total,
                'status': f'Enviando o produto {p["sku"]}'
            }
        )

        try:
            Log.info(f'[PREÇO] Iniciando o envio do item {p["sku"]}.')
            updateProduct(
                sku=p['sku'],
                data=p['data']
            )
            Log.info(f'[PREÇO]------ Enviado para o site')

            concluidos += 1

        except Exception as e:
            erros_count += 1
            erros.append(f'Produto: {p["sku"]} -------- Erro: {e}')

            Log.error(
                f'[PREÇO] Erro ao enviar o produto {p["sku"]} erro: {e}')

        count += 1

    Log.info(f'[PREÇO] Envio de produtos finalizado.')
    Log.info(f'[PREÇO] Salvando data e hora da sincronização.')

    with app.app_context():
        db.engine.dispose()  # corrigi o erro do postgres
        config.dtsincr_preco = dthr_sincr
        config.update()

    return {
        'name': format_task_name(self.name),
        'complete': concluidos,
        'errors_count': erros_count,
        'errors': erros,
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.task(bind=True, name='atualizar-promocao')
def atualiza_promocoes_task(self):
    """
        cria uma tarefa para atualizar as promoções dos produtos no site

        Raises
        -----------
        Fault<sku já existe no site>
            Exceção lançada quando o produto já existe no site
    """

    Log.info(f'[PROMOÇÃO] Iniciando o envio dos produtos.')

    config = ConfigMagento.by_id(1)
    dthr_sincr = datetime.now()
    produtos = buscar_produtos_promocao(dthr_sincr=config.dtsincr_promocao)
    produtos = converte_produtos_promocao(produtos)

    concluidos = 0
    erros_count = 0
    erros = []
    count = 0
    total = len(produtos)

    for p in produtos:
        self.update_state(
            state='PROGRESS',
            meta={
                'name': format_task_name(self.name),
                'complete': concluidos,
                'errors_count': erros_count,
                'errors': erros,
                'current': count,
                'total': total,
                'status': f'Enviando o produto {p["sku"]}'
            }
        )

        try:
            Log.info(f'[PROMOÇÃO] Iniciando o envio do item {p["sku"]}.')
            updateProduct(
                p['sku'],
                p['data']
            )
            Log.info(f'[PROMOÇÃO]------ Enviado para o site')

            concluidos += 1

        except Exception as e:
            erros_count += 1
            erros.append(f'Produto: {p["sku"]} -------- Erro: {e}')

            Log.error(
                f'[PROMOÇÃO] Erro ao enviar o produto {p["sku"]} erro: {e}')

        count += 1

    Log.info(f'[PROMOÇÃO] Envio de produtos finalizado.')
    Log.info(f'[PROMOÇÃO] Salvando data e hora da sincronização.')

    with app.app_context():
        db.engine.dispose()  # corrigi o erro do postgres
        config.dtsincr_promocao = dthr_sincr
        config.update()

    return {
        'name': format_task_name(self.name),
        'complete': concluidos,
        'errors_count': erros_count,
        'errors': erros,
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.task(bind=True, name='inativar')
def inativar_task(self):
    """
        cria uma tarefa para atualizar os produtos inativos no site

        Raises
        -----------
        Fault<sku já existe no site>
            Exceção lançada quando o produto já existe no site
    """
    
    with app.app_context():
        Log.info(f'[INATIVAR] Iniciando o envio dos produtos.')
        db.engine.dispose()

        config = ConfigMagento.by_id(1)
        dthr_sincr = datetime.now()
        produtos_erp = buscar_produtos_inativos()
        # produtos = converte_produto_inativo(produtos)

        # Variáveis utilizadas para atualizar a barra de
        # progresso na tela do usuário
        concluidos = 0
        erros_count = 0
        erros = []
        count = 0
        total = len(produtos_erp)

        for produto_erp in produtos_erp:
            sku = produto_erp.idsubproduto
            
            self.update_state(
                state='PROGRESS',
                meta={
                    'name': format_task_name(self.name),
                    'complete': concluidos,
                    'errors_count': erros_count,
                    'errors': erros,
                    'current': count,
                    'total': total,
                    'status': f'Enviando o produto {sku}'
                }
            )

            try:
                Log.info(f'[INATIVAR] Iniciando o envio do item {sku}.')

                mag_produto = converte_produto_inativo(produto_erp)
                updateProduct(
                    mag_produto['sku'],
                    mag_produto['data']
                )
                Log.info(f'[INATIVAR]------ Enviado para o site')

                # pega o tipo e se esta inativo do ERP
                tipo, inativo = produto_erp.idtipo, produto_erp.flaginativo

                # verifica se o produto foi ativado ou inativado no site
                if tipo == 2 and inativo == 'T':
                    produto_erp.idtipo = 3
                elif tipo == 3 and inativo == 'F':
                    produto_erp.idtipo = 2

                produto_erp.update()

                Log.info(f'[INATIVAR]------ Gravado no ERP.')

                concluidos += 1

            except Exception as e:
                erros_count += 1
                erros.append(f'Produto: {sku} -------- Erro: {e}')

                Log.error(
                    f'[INATIVAR] Erro ao enviar o produto {sku} erro: {e}')

            count += 1

        Log.info(f'[INATIVAR] Envio de produtos finalizado.')
        Log.info(f'[INATIVAR] Salvando data e hora da sincronização.')

        config.dtsincr_inativos = dthr_sincr
        config.update()

    return {
        'name': format_task_name(self.name),
        'complete': concluidos,
        'errors_count': erros_count,
        'errors': erros,
        'current': total,
        'total': total,
        'status': 'complete'
    }


@mycelery.on_after_configure.connect
def periodic_tasks(sender, **kwargs):
    """
        Confira as tarefas para serem executadas no tempo determinado
    """

    # (atualiza_precos_task) executado de segunda a sabado aos 15 minutos
    # das horas 0, 11 e 17
    sender.add_periodic_task(
        crontab(minute=15, hour=[0, 11, 17], day_of_week='mon-sat'),
        atualiza_precos_task)

    # (atualiza_estoque_task) executado de segunda a sabado aos 45 minutos
    # das horas 0, 8, 14 e 19
    sender.add_periodic_task(
        crontab(minute=45, hour=[0, 8, 14, 19], day_of_week='mon-sat'),
        atualiza_estoque_task)    

    # (inativar_task) executado de segunda a sabado às 20:15
    sender.add_periodic_task(
        crontab(minute=15, hour=20, day_of_week='mon-sat'), inativar_task)
