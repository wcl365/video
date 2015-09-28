__author__ = 'fyz'

from sqlalchemy import create_engine

URI = "mysql+oursql://root@localhost/video"


class _DBConnector(object):
    def __init__(self):
        self.engine = create_engine(URI)


engine = _DBConnector().engine
