from app.application import db
from datetime import date, datetime


class MagSincronizacao(db.Model):
    """
        Contem os dados das ultima sincronizacoes
        com o magento
    """
    __tablename__ = 'mag_sincronizacao'

    sinc_id = db.Column(db.Integer, primary_key=True)
    dthr_preco = db.Column(db.DateTime())
    dthr_estoque = db.Column(db.DateTime())


class MagProduto(db.Model):
    """
        representa as categorias do magento
        sendo a seção a categoria primaria
        o grupo a categoria secundária e o
        subgrupo a terciaria.
    """
    __tablename__ = 'mag_produtos'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer, unique=True)
    dt_estoque = db.Column(db.DateTime())
    dt_preco = db.Column(db.DateTime())
    inativo = db.Column(db.Boolean(), default=True)
    possui_imagem = db.Column(db.Boolean())
    atualiza_imagem = db.Column(db.Boolean())
    idsecao = db.Column(db.Integer)
    idgrupo = db.Column(db.Integer)
    idsubgrupo = db.Column(db.Integer)
    send_at = db.Column(db.DateTime(), default=datetime.now)
    update_at = db.Column(db.DateTime(), onupdate=datetime.now)


class MagCategoriaProduto(db.Model):
    """
        representa as categorias do magento
        sendo a seção a categoria primaria
        o grupo a categoria secundária e o
        subgrupo a terciaria.
    """
    __tablename__ = 'mag_categorias_produtos'

    sku = db.Column(db.Integer, primary_key=True)
    secao = db.Column(db.String(60))
    grupo = db.Column(db.String(60))
    subgrupo = db.Column(db.String(60))
    create_at = db.Column(db.Date(), default=datetime.now)
    update_at = db.Column(db.Date(), onupdate=datetime.now)


class MagErrosProdutos(db.Model):
    """
        representa os erros gerados ao
        realizar ações de cadastro de
        informações de produtos no
        integrador.
    """
    __tablename__ = 'mag_error_produtos'

    id_erro = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.Integer)
    origem = db.Column(db.String(40))
    message = db.Column(db.String(100))
    update_at = db.Column(
        db.DateTime(),
        default=datetime.now,
        onupdate=datetime.now
    )
    

class CissProduto(db.Model):
    """"""
    __tablename__ = 'PRODUTO'
    __bind_key__ = 'ciss'

    idproduto = db.Column(db.Integer, primary_key=True)
    descrcomproduto = db.Column(db.String(60))
    fabricante = db.Column(db.String(40))
    embalagemsaida = db.Column(db.String(2), db.ForeignKey(
        'PRODUTO_EMBALAGEM.unidadeembalagem'))
    
    embalagem = db.relationship('CissEmbalagens')


class CissEmbalagens(db.Model):
    """"""
    __tablename__ = 'PRODUTO_EMBALAGEM'
    __bind_key__ = 'ciss'

    unidadeembalagem = db.Column(db.String(2), primary_key=True)
    descrembalagem = db.Column(db.String(40))


class CissProdutoGrade(db.Model):
    """"""
    __tablename__ = 'PRODUTO_GRADE'
    __bind_key__ = 'ciss'

    idproduto = db.Column(db.ForeignKey('PRODUTO.idproduto'), primary_key=True)
    idsubproduto = db.Column(db.Integer, primary_key=True)
    subdescricao = db.Column(db.String(100))
    descrresproduto = db.Column(db.String(60))
    codbar = db.Column(db.String(20))
    idmodelo = db.Column(db.Integer)
    idtipo = db.Column(db.Integer)
    pesoliquido = db.Column(db.Numeric(12,3))
    valmultivendas = db.Column(db.Numeric(12,3))
    dtcadastro = db.Column(db.Date())
    flaginativo = db.Column(db.String(1), db.CheckConstraint(
        "flag_carga_media=='T' or flag_carga_media=='F'"))

    produto = db.relationship('CissProduto')

    join2 = "and_("
    join2 = join2 + "CissProdutoEstoque.idproduto==CissProdutoGrade.idproduto,"
    join2 = join2 + "CissProdutoEstoque.idsubproduto==CissProdutoGrade.idsubproduto,"
    join2 = join2 + "CissProdutoEstoque.idlocalestoque==1,"
    join2 = join2 + "CissProdutoEstoque.qtdatualestoque==0,"
    join2 = join2 + "CissProdutoEstoque.idempresa==2)"

    zerados = db.relationship(
        'CissProdutoEstoque',
        primaryjoin=join2
    )


class CissProdutoEstoque(db.Model):
    """"""
    __tablename__ = 'ESTOQUE_SALDO_ATUAL'
    __bind_key__ = 'ciss'

    idproduto = db.Column(db.ForeignKey('PRODUTO_GRADE.idproduto'), 
                          primary_key=True)
    idsubproduto = db.Column(db.ForeignKey('PRODUTO_GRADE.idsubproduto'), 
                          primary_key=True)
    idlocalestoque = db.Column(db.Integer, primary_key=True)
    idempresa = db.Column(db.Integer, primary_key=True)
    qtdatualestoque = db.Column(db.Numeric(12,3))
    dtalteracao = db.Column(db.DateTime())

    join = "and_("
    join = join + "CissProdutoEstoque.idproduto==CissProdutoGrade.idproduto,"
    join = join + "CissProdutoEstoque.idsubproduto==CissProdutoGrade.idsubproduto,"
    join = join + "CissProdutoEstoque.idlocalestoque==1,"
    join = join + "CissProdutoEstoque.idempresa==2)"

    produto = db.relationship(
        'CissProdutoGrade',
        backref=db.backref('saldo', uselist=False),
        primaryjoin=join
    )


class CissProdutoPreco(db.Model):
    """"""
    __tablename__ = 'POLITICA_PRECO_PRODUTO'
    __bind_key__ = 'ciss'

    idproduto = db.Column(
        db.ForeignKey('PRODUTO_GRADE.idproduto'), 
        primary_key=True
    )
    idsubproduto = db.Column(
        db.ForeignKey('PRODUTO_GRADE.idsubproduto'), 
        primary_key=True
    )
    idempresa = db.Column(db.Integer, primary_key=True)
    valprecovarejo = db.Column(db.Numeric(15, 6))
    valpromvarejo = db.Column(db.Numeric(15, 6))
    dtalteracaovar = db.Column(db.DateTime())
    dtalteracaopromovar = db.Column(db.DateTime())
    dtinipromocaovar = db.Column(db.Date())
    dtfimpromocaovar = db.Column(db.Date())

    join = "and_("
    join = join + "CissProdutoPreco.idproduto==CissProdutoGrade.idproduto,"
    join = join + "CissProdutoPreco.idsubproduto==CissProdutoGrade.idsubproduto,"
    join = join + "CissProdutoPreco.idempresa==2)"

    produto = db.relationship(
        'CissProdutoGrade',
        backref=db.backref('preco', uselist=False),
        primaryjoin=join
    )
