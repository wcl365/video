__author__ = 'fyz'

from DBConnector import engine
import time
import requests
import hashlib
import json
import logging

from common import env
env.loadEnv()

class BaseModel(object):
    def execute(self, sql, *params):
        sql = sql % self.__tablename__
        logging.debug(sql)
        return engine.execute(sql, *params)

    def fetch(self, sql, *params):
        sql = sql % self.__tablename__
        logging.debug(sql)
        res = engine.execute(sql, *params)
        if not res:
            return []
        li = []
        for row in res:
            tmp = dict(zip(res.keys(), row))
            li.append(tmp)
        return li

    def one(self, sql, *params):
        sql = sql % self.__tablename__
        logging.debug(sql)
        res = engine.execute(sql, *params)
        if not res:
            return None
        li = []
        for row in res:
            tmp = dict(zip(res.keys(), row))
            li.append(tmp)
        if len(li) > 1 or len(li) == 0:
            raise Exception("multi rows")
        return li[0]


def cur_ts():
    return int(time.time() * 1000)


class DramaModel(BaseModel):
    __tablename__ = "drama"

    def insert(self, name, year, poster, actor, desc, href):
        sql = "insert into %s (`name`, `poster`, `year`, `time_created`, `actors`, `description`, `source`) values (?, ?, ?, ?, ?, ?, ?)"
        self.execute(sql, name, poster, year, cur_ts(), actor, desc, href)

    def list(self):
        sql = "select * from %s"
        return self.fetch(sql)

    def get_by_id(self, id):
        sql = "SELECT * FROM %s WHERE id=?"
        return self.one(sql, id)

    def get_by_name(self, name):
        sql = "select * from %s where name = ? limit 1"
        x =  self.fetch(sql, name)
        if x:
            return x[0]

    def list_avalable(self, limit, offset):
        sql = "select * from %s where id in (select DISTINCT(drama_id) from drama_episode) order by year desc limit ? offset ?"
        return self.fetch(sql, limit, offset)

class DramaEpisodeModel(BaseModel):
    __tablename__ = 'drama_episode'

    def insert(self, drama_id, episode, time_release, source, url, hd_url):
        sql = "insert ignore into %s (drama_id, episode, time_release, `source`, `url`, `hd_url`, time_created) values (?, ?, ?, ?, ?, ?, ?)"
        self.execute(sql, drama_id, episode, time_release, source, url, hd_url, cur_ts())

    def get_by_drama_id(self, drama_id):
        sql = "select * from %s where drama_id = ? order by episode"
        return self.fetch(sql, drama_id)


class UrlContentModel(BaseModel):
    __tablename__ = 'url_content'

    def insert(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            logging.error("get content error: %s" % url)
            return -1
        content = resp.content
        if len(content) < 500:
            logging.error("get content error, maybe empty : %s, %s" % url, content)
            return -1
        m = hashlib.md5()
        m.update(content)
        hash_value = m.hexdigest()

        sql = "insert ignore into %s values (null, ?, ?, ?)"
        value = self.execute(sql, url, hash_value, content)
        if value.rowcount == 0:
            logging.info("dupliate url, %s" % url)
            return 0
        return 1

class DramaGetStrategyModel(BaseModel):
    __tablename__ = 'drama_get_strategy'

    def insert(self, drama_id, source, strategy):
        if not strategy:
            return
        sql = "insert into %s (drama_id, `source`, strategy, time_created) values (?, ?, ?, ?)"
        self.execute(sql, drama_id, source, json.dumps(strategy), cur_ts())

    def get_by_drama_id(self, drama_id):
        sql = "select * from %s where drama_id = ? limit 1"
        s = self.one(sql, drama_id)
        if not s:
            return None, None
        return s['source'], json.loads(s['strategy'])

class DramaInfoModel(BaseModel):
    __tablename__ = 'drama_info'

    def insert(self, drama_id, info):
        if not isinstance(info, str):
            info = json.dumps(info)
        sql = "insert into %s (drama_id, `info`) values (?, ?)"
        self.execute(sql, drama_id, info)

    def get_by_drama_id(self, drama_id):
        sql = "select * from %s where drama_id = ? limit 1"
        s = self.one(sql, drama_id)
        return s

dramaModel = DramaModel()
dramaEpisodeModel = DramaEpisodeModel()
ucModel = UrlContentModel()
dramaInfoModel = DramaInfoModel()
