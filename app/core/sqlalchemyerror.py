from sqlalchemy import event


def sqlalchemyErrorHandler(db):
    @event.listens_for(db.engine, "checkout")
    def ping_connection(dbapi_connection, connection_record, connection_proxy):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("SELECT 1")
        except:
            # optional - dispose the whole pool
            # instead of invalidating one at a time
            # connection_proxy._pool.dispose()

            # raise DisconnectionError - pool will try
            # connecting again up to three times before raising.
            raise exc.DisconnectionError()
        cursor.close()