import logging
from logging.handlers import TimedRotatingFileHandler


class Log():
    """
        Classe utilizada para registrar os Logs das tarefas

        A classe Log é utilizada para registrar os logs das tarefas
        executadas para consulta posterior do que foi feito. Registra
        tanto os que foi feito quanto os erros capturados

        Attributes
        -----------
        _info (privado)
            atributo estatico e privado para registrar o log das informações
            do que foi feito no integrador

        _error (privado)
            atributo estatico e privado para registrar o log de erros
            levantados pelo sistema na hora da execução das tarefas

        Methods
        -----------
        info(message)
            método estatico utlizado para registrar os logs das tarefas
            executadas. Cria um novo logger se ainda nao existir atribui
            ao atributo _info.

        error(message)
            método estatico utlizado para registrar os logs de erros
            levantados na execução das tarefas. Cria um novo logger
            se ainda nao existir atribui ao atributo _error.

        create_log(name, level, formatter, filename)
            método utilizado internamente para criar um logger a partir
            dos parametros informados. retorna o logger criado.
    """

    _info = None
    _error = None

    @staticmethod
    def info(message):
        if not Log._info:
            Log._info = Log.create_log(
                'appinfo',
                logging.INFO,
                '%(message)s:%(asctime)s:%(name)s',
                './logs/info.log'
            )
        Log._info.info(msg=message)

    @staticmethod
    def error(message):
        if not Log._error:
            Log._error = Log.create_log(
                'apperror',
                logging.ERROR,
                '%(message)s:%(asctime)s:%(name)s',
                './logs/error.log'
            )
        Log._error.error(msg=message)

    @staticmethod
    def create_log(name, level, formatter, filename):
        # Cria o log para registrar os processos de sincronização
        log = logging.getLogger(name)
        log.setLevel(level)

        # Cria o handler para configurar o path do arquivo de log com rotação
        timehandler = TimedRotatingFileHandler(
            filename, when='w6', interval=1, backupCount=5)
        formatter = logging.Formatter(formatter)
        timehandler.setFormatter(formatter)
        log.addHandler(timehandler)

        return log
