__author__ = 'fyz'

import requests
import hashlib
import json
import logging
from skyb import cur_ms, MysqlEngine, Singleton


class BaseModel(Singleton):
    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    def setup_all_model(engine):
        DramaModel(engine)
        DramaEpisodeModel(engine)
        UrlContentModel(engine)
        DramaGetStrategyModel(engine)
        DramaInfoModel(engine)


class DramaModel(BaseModel):
    __tablename__ = "drama"

    def insert(self, name, year, poster, actor, desc, href, score=0):
        sql = "insert into drama (`name`, `poster`, `year`, `time_created`, `actors`, `description`, `source`, `score`) values (?, ?, ?, ?, ?, ?, ?, ?)"
        self.engine.execute(sql, (name, poster, year, cur_ms(), actor, desc, href, score))

    def set_score(self, id, score):
        sql = "update drama set score=? where id=?"
        self.engine.execute(sql, (score, id))

    def list(self):
        sql = "select * from drama"
        return self.engine.fetch_row(sql)

    def get_by_id(self, id):
        sql = "SELECT * FROM drama WHERE id=?"
        return self.engine.fetchone_row(sql, (id,))

    def get_by_name(self, name):
        sql = "select * from drama where name = ? limit 1"
        x = self.engine.fetch_row(sql, (name,))
        if x:
            return x[0]

    def search_by_name(self, name, count=20):
        if len(name) == 0:
            return []
        match_str = '%%%s%%' % name
        sql = "select * from drama where id in (select DISTINCT(drama_id) from drama_episode) and (name like ? or actors like ?) order by year desc limit ?"
        return self.engine.fetch_row(sql, (match_str, match_str, count))

    def list_avalable(self, limit, offset):
        sql = "select * from drama where id in (select DISTINCT(drama_id) from drama_episode) order by year desc limit ? offset ?"
        return self.engine.fetch_row(sql, (limit, offset))


class DramaEpisodeModel(BaseModel):
    __tablename__ = 'drama_episode'

    def insert(self, drama_id, episode, time_release, source, url, hd_url):
        sql = "insert ignore into drama_episode (drama_id, episode, time_release, `source`, `url`, `hd_url`, time_created) values (?, ?, ?, ?, ?, ?, ?)"
        self.engine.execute(sql, (drama_id, episode, time_release, source, url, hd_url, cur_ms()))

    def get_by_drama_id(self, drama_id):
        sql = "select * from drama_episode where drama_id = ? order by episode"
        return self.engine.fetch_row(sql, (drama_id,))

    def update_url(self, id, url, hd_url):
        sql = "update drama_episode set url=?, hd_url=? where id=?"
        return self.engine.execute(sql, (url, hd_url, id))

    def new_drama(self, count):
        sql = "select drama_id, max(episode) as episode from drama_episode group by drama_id order by time_created desc limit ?"
        return self.engine.fetch_row(sql, (count,))


class UrlContentModel(BaseModel):
    __tablename__ = 'url_content'

    def insert(self, url):
        resp = requests.get(url)
        if resp.status_code != 200:
            logging.error("get content error: %s" % url)
            return -1
        content = resp.content
        if len(content) < 500:
            logging.error("get content error, maybe empty : %s, %s" % (url, content))
            return -1
        m = hashlib.md5()
        m.update(content)
        hash_value = m.hexdigest()

        '''
        if appConfig.get('storeUrlContent'):
            sql = "insert ignore into %s values (null, ?, ?, ?)"
            value = self.execute(sql, url, hash_value, content)
            if value.rowcount == 0:
                logging.info("dupliate url, %s" % url)
                return 0
        '''
        return 1


class DramaGetStrategyModel(BaseModel):
    __tablename__ = 'drama_get_strategy'

    def insert(self, drama_id, source, strategy):
        if not strategy:
            return
        sql = "insert into drama_get_strategy (drama_id, `source`, strategy, time_created) values (?, ?, ?, ?)"
        self.engine.execute(sql, (drama_id, source, json.dumps(strategy), cur_ms()))

    def get_by_drama_id(self, drama_id):
        sql = "select * from drama_get_strategy where drama_id = ? limit 1"
        s = self.engine.fetchone_row(sql, drama_id)
        if not s:
            return None, None
        return s['source'], json.loads(s['strategy'])


class DramaInfoModel(BaseModel):
    __tablename__ = 'drama_info'

    def insert(self, drama_id, info):
        if not isinstance(info, str):
            info = json.dumps(info)
        sql = "insert into drama_info (drama_id, `info`) values (?, ?)"
        self.engine.execute(sql, (drama_id, info))

    def get_by_drama_id(self, drama_id):
        sql = "select * from drama_info where drama_id = ? limit 1"
        s = self.engine.fetchone_row(sql, (drama_id,))
        return s
