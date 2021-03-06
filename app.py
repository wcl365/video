# -*- coding: utf-8 -*-

import os, os.path
import argparse

from skyb.quick.tornado import BaseApplication, BaseAuthHandler
from skyb import load_configuration, MysqlEngine

from model.models import DramaModel, DramaEpisodeModel, BaseModel
from service import DramaService

from wechat.basic import WechatBasic
from wechat.messages import *
from hashids import Hashids
from parser.tudou import TudouParser


class Application(BaseApplication):
    def __init__(self, conf, debug=False):
        handlers = [
            ('/', IndexHandler),
            ('/admin/drama/add', AdminDramaAddHandler),
            ('/admin/drama/list', AdminDramaListHandler),
            ('/admin/drama/search', AdminDramaSearchHandler),
            ('/admin/drama/parser', AdminDramaParserHandler),

            ('/api/drama/list', ApiDramaListHandler),
            ('/api/drama/search', ApiDramaSearchHandler),

            ('/drama/episode/play/(\S+)', DramaEpisodePlayHandler),
            ('/drama/episode/(\S+)', DramaEpisodeHandler),

            ('/weixin', WeixinHandler),
        ]
        settings = dict(template_path=os.path.join(os.path.dirname(__file__), "./web/template"),
                        static_path=os.path.join(os.path.dirname(__file__), "./web/static"),
                        debug=debug,
                        autoescape=None
                        )
        self.conf = conf
        engine = MysqlEngine(conf.get('db.uri'))

        BaseModel.setup_all_model(engine)

        self.dramaModel = DramaModel.instance()
        self.episodeModel = DramaEpisodeModel.instance()

        self.dramaService = DramaService()
        self.wechat = WechatBasic(token=conf.get("wechat.token"), appid=conf.get("wechat.appId"),
                                  appsecret=conf.get("wechat.appSecret"))
        self.hashid = Hashids(salt="woshifyz")
        self.parser = {
            'tudou': TudouParser()
        }
        super(Application, self).__init__(handlers, **settings)


class BaseHandler(BaseAuthHandler):
    def encode(self, *ids):
        assert len(ids) > 0
        return self.application.hashid.encode(*ids)

    def decode(self, h_str):
        return self.application.hashid.decode(h_str)

    def decodeOne(self, h_str):
        return self.decode(h_str)[0]


class AdminBaseHandler(BaseHandler):
    def __init__(self, *args, **kw):
        super(AdminBaseHandler, self).__init__(*args, **kw)
        self._auth = self.application.conf.get("server.http.password")


class AdminDramaAddHandler(AdminBaseHandler):
    def get(self):
        self.render("admin_drama_add.html")

    def post(self):
        name = self.get_argument("name").strip()
        desc = self.get_argument("desc").strip()
        actors = self.get_argument("actors").strip()
        poster = self.get_argument("poster").strip()
        year = int(self.get_argument("year"))
        assert len(name) > 0
        assert len(desc) > 0
        assert len(actors) > 0
        assert len(poster) > 0
        self.application.dramaModel.insert(name, year, poster, actors, desc, "", 0)
        self.write("success")


class AdminDramaListHandler(AdminBaseHandler):
    def get(self):
        page = int(self.get_argument("page", 0))
        count = int(self.get_argument("count", 20))

        dramas = self.application.dramaService.get_drama_infos(count, page * count)
        for d in dramas:
            d['hash_code'] = self.encode(d['id'])
        self.render("drama_list.html", dramas=dramas)


class AdminDramaSearchHandler(AdminBaseHandler):
    def get(self):
        name = self.get_argument("name", "").strip()
        count = int(self.get_argument("count", 20))
        if len(name) == 0:
            dramas = []
        else:
            dramas = self.application.dramaService.search_by_name(name, count)
        self.render('drama_list.html', dramas=dramas)


class AdminDramaParserHandler(AdminBaseHandler):
    def get(self):
        drama_id = int(self.get_argument("drama_id"))
        self.render("admin_parser.html", drama_id=drama_id)

    def post(self):
        channel = self.get_argument('channel')
        drama_id = int(self.get_argument('drama_id'))
        episode = int(self.get_argument('episode'))
        url = self.get_argument('url')

        url, hd_url = self.application.parser.get(channel).parse(url)
        if not (url and hd_url):
            self.write("error")
        else:
            self.application.episodeModel.insert(drama_id, episode, 0, "", url, hd_url)
            self.write("success \n%s\n%s" % (url, hd_url))


class ApiDramaListHandler(BaseHandler):
    def get(self):
        page = int(self.get_argument("page", 0))
        count = int(self.get_argument("count", 20))
        dramas = self.application.dramaService.get_drama_infos(count, page * count)
        self.write({"videos": dramas})


class ApiDramaSearchHandler(BaseHandler):
    def get(self):
        name = self.get_argument("name", "").strip()
        count = int(self.get_argument("count", 20))
        if len(name) == 0:
            dramas = []
        else:
            dramas = self.application.dramaService.search_by_name(name, count)
        self.write({"videos": dramas})


class DramaEpisodeHandler(BaseHandler):
    def get(self, drama_id):
        drama_id = self.decodeOne(drama_id)
        episodes = self.application.episodeModel.get_by_drama_id(drama_id)
        self.render("episode.html", episodes=episodes)


class DramaEpisodePlayHandler(BaseHandler):
    def get(self, drama_ep_id):
        drama_id, ep_id = self.decode(drama_ep_id)
        drama = self.application.dramaModel.get_by_id(int(drama_id))
        if not drama:
            self.write(u"节目不存在")
        episodes = self.application.episodeModel.get_by_drama_id(int(drama_id))
        for ep in episodes:
            ep['hash_code'] = self.encode(drama_id, ep['episode'])
        self.render("episode_play.html", ep=episodes[int(ep_id) - 1], eps=episodes, drama=drama)


class IndexHandler(BaseHandler):
    def get(self):
        self.redirect("/admin/drama/list")


class WeixinHandler(BaseHandler):
    def get(self):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")
        if self.application.wechat.check_signature(signature, timestamp, nonce):
            self.write(echostr)
        else:
            self.write("error")

    def post(self):
        self.application.wechat.parse_data(self.request.body)
        message = self.application.wechat.get_message()

        if isinstance(message, EventMessage) and message.type == 'subcribe':
            response = self.application.wechat.response_text("感谢关注, 我们会每天给你推荐你最感兴趣的演出! (。・`ω´・)")
        elif isinstance(message, TextMessage) and (message.content.strip() == 'new'):
            eps = self.application.dramaService.new_drama()
            content = []
            for ep in eps:
                tmp = {
                    'title': u'%s  第%s集' % (ep['drama']['name'], ep['episode']),
                    'description': ep['drama']['description'],
                    'picurl': ep['drama']['poster'],
                    'url': u'%s%s%s' % (
                        self.application.conf.get("server.host"), '/drama/episode/play/',
                        self.encode(ep['drama_id'], ep['episode']))
                }
                content.append(tmp)
            if len(content) == 0:
                response = self.application.wechat.response_text("没有最新的结果")
            else:
                response = self.application.wechat.response_news(content)
        elif isinstance(message, TextMessage) and (
                    message.content.startswith("search") or message.content.startswith("ss")):
            value = message.content.split()
            keyword = ' '.join(value[1:])
            dramas = self.application.dramaService.search_by_name(keyword, count=8)
            content = []
            for d in dramas:
                tmp = {
                    'title': u'%s  第%s集' % (d['name'], 1),
                    'description': d['description'],
                    'picurl': d['poster'],
                    'url': u'%s%s%s' % (
                        self.application.conf.get("server.host"), '/drama/episode/play/', self.encode(d['id'], 1))
                }
                content.append(tmp)
            if len(content) == 0:
                response = self.application.wechat.response_text("没有结果, 你可以尝试换个名称或者演员搜索")
            else:
                response = self.application.wechat.response_news(content)
        else:
            response = self.application.wechat.response_text("这里主要分享一些影视资源\n输入:\n\nss 关键字\n\n搜索资源")
        self.write(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config')
    parser.add_argument('-p', '--port')
    parser.add_argument('-d', action="store_true", help="whether to turn on debug mode")
    args, _ = parser.parse_known_args()
    Application(load_configuration(args.config), args.d).boot(args.port)
