# -*- coding: utf-8 -*-

import os, os.path
import tornado.ioloop
import tornado.web
import argparse

from model.models import DramaModel, DramaEpisodeModel, dramaEpisodeModel
from service import DramaService
from common import appConfig

from wechat.basic import WechatBasic
from wechat.messages import *
from hashids import Hashids


class Application(tornado.web.Application):
    def __init__(self, mode, debug=False):
        handlers = [
            ('/', IndexHandler),
            ('/admin/drama/list', DramaListHandler),

            ('/api/drama/list', ApiDramaListHandler),
            ('/api/drama/search', ApiDramaSearchHandler),

            ('/drama/episode/play/(\S+)', DramaEpisodePlayHandler),
            ('/drama/episode/(\S+)', DramaEpisodeHandler),

            ('/weixin', WeixinHandler),
        ]
        settings = dict(template_path=os.path.join(os.path.dirname(__file__), "./template"),
                        static_path=os.path.join(os.path.dirname(__file__), "./static"),
                        debug=True,
                        autoescape=None
                        )
        self.mode = mode
        self.dramaModel = DramaModel()
        self.episodeModel = DramaEpisodeModel()
        self.dramaService = DramaService()
        self.wechat = WechatBasic(token=appConfig.get("wechat.token"), appid=appConfig.get("wechat.appId"),
                          appsecret=appConfig.get("wechat.appSecret"))
        self.hashid = Hashids(salt="woshifyz")
        super(Application, self).__init__(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def encode(self, *ids):
        assert len(ids) > 0
        return self.application.hashid.encode(*ids)

    def decode(self, h_str):
        return self.application.hashid.decode(h_str)

    def decodeOne(self, h_str):
        return self.decode(h_str)[0]

class DramaListHandler(BaseHandler):
    def get(self):
        page = int(self.get_argument("page", 0))
        count = int(self.get_argument("count", 20))

        dramas = self.application.dramaService.get_drama_infos(count, page * count)
        for d in dramas:
            d['hash_code'] = self.encode(d['id'])
        self.render("drama_list.html", dramas=dramas)

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
        self.render("episode_play.html", ep = episodes[int(ep_id) - 1], eps=episodes, drama=drama)

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
        elif isinstance(message, TextMessage) and (message.content.startswith("search") or message.content.startswith("ss")):
            value = message.content.split()
            keyword = ' '.join(value[1:])
            dramas = self.application.dramaService.search_by_name(keyword, count=8)
            content = []
            for d in dramas:
                tmp = {
                    'title': u'%s  第%s集' % (d['name'], 1),
                    'description': d['description'],
                    'picurl': d['poster'],
                    'url': u'%s%s%s' % (appConfig.get("server.host"), '/drama/episode/play/', self.encode(d['id'], 1))
                }
                content.append(tmp)
            if len(content) == 0:
                response = self.application.wechat.response_text("没有结果, 你可以尝试换个名称或者演员搜索")
            else:
                response = self.application.wechat.response_news(content)
        else:
            response = self.application.wechat.response_text("感谢发送")
        self.write(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', default=8080, help="server port")
    parser.add_argument('-d', action="store_true", help="whether to turn on debug mode")
    parser.add_argument('-m', '--mode', default='local', help="run mode")
    args = parser.parse_args()
    application = Application(args.mode, args.d)
    application.listen(args.port)
    print 'application start at port %s' % args.port
    tornado.ioloop.IOLoop.instance().start()
