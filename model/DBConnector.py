__author__ = 'fyz'

from sqlalchemy import create_engine
from common import appConfig

class _DBConnector(object):
    def __init__(self):
        self.engine = create_engine(appConfig.get('db.uri'))


engine = _DBConnector().engine
