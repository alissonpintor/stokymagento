from flask_restful import Resource, reqparse
from app.models.categorias import MagCategorias


OPERATORS = {
    'eq': '==',
    'lt': '<',
    'gt': '>'
}


class Categoria(Resource):
    """
    Classe usada para representar a api das categorias do site

    Attributes
    --------------
    parser: RequestParser
        usado para criar os parametros

    Methods
    --------------
    get(id)
        retorna a categoria desejada a partir do id (None se nao existe)    

    Raises
    --------------
    ErrosRetornados
        erros retornados pela api
    """

    parser = reqparse.RequestParser()
    parser.add_argument(
        'category_id',
        type=int,
        required=True,
        help="Este campo nao pode ficar em branco!"
    )
    parser.add_argument(
        'name',
        type=str,
        required=True,
        help="Este campo nao pode ficar em branco!"
    )
    parser.add_argument(
        'parent_id',
        type=int,
        required=True,
        help="Este campo nao pode ficar em branco!"
    )

    def get(self, id):
        """
            retorna a categoria desejada a partir do id (None se nao existe)
        """

        categoria = MagCategorias.by(category_id=id)

        if categoria:
            return categoria.json(), 200
        return {'message': 'O Item não existe'}, 404


class CategoriaList(Resource):
    """
    Classe usada para representar a api de uma lista de categorias

    Attributes
    --------------

    Methods
    --------------
    get()
        retorna a lista de categorias existentes (None se nao existe)   

    Raises
    --------------
    """
    parser = reqparse.RequestParser()
    parser.add_argument(
        'q',
        type=str
    )

    def get(self):
        """
            retorna a lista de categorias existentes (None se nao existe)
        """

        categorias = self.convert(2)
        return categorias, 200

    def convert(self, parent_id):
        """
            converte a lista de categorias em formato treeview
        """

        lista = []
        categorias = MagCategorias.by(get_first=False, parent_id=parent_id)
        for c in categorias:
            childrens = self.convert(c.category_id)
            c = c.json()
            if childrens:
                c['childrens'] = childrens
            lista.append(c)
        
        return lista
    
    def get_query(self, raw_query):
        """
            Recebe o query enviada pelo usuario e converte para ser usado
            na query como o ORM
        """
        print(raw_query)
        raw_query = raw_query.split('&')

        for query in raw_query:
            print(query)

