# -*- coding: utf-8 -*-

import os, os.path
import tornado.ioloop
import tornado.web
import argparse

from model.models import DramaModel, DramaEpisodeModel, dramaEpisodeModel
from service import DramaService


class Application(tornado.web.Application):
    def __init__(self, mode, debug=False):
        handlers = [
            ('/', IndexHandler),
            ('/drama/list', DramaListHandler),
            ('/drama/episode/(\d+)', DramaEpisodeHandler),
            ('/drama/episode/(\d+?)/(\d+?)', DramaEpisodePlayHandler),


            ('/api/drama/list', ApiDramaListHandler),
            ('/api/drama/search', ApiDramaSearchHandler),
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
        super(Application, self).__init__(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    pass

class DramaListHandler(BaseHandler):
    def get(self):
        page = int(self.get_argument("page", 0))
        count = int(self.get_argument("count", 20))

        dramas = self.application.dramaService.get_drama_infos(count, page * count)
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
        episodes = self.application.episodeModel.get_by_drama_id(drama_id)
        self.render("episode.html", episodes=episodes)

class DramaEpisodePlayHandler(BaseHandler):
    def get(self, drama_id, ep):
        episodes = self.application.episodeModel.get_by_drama_id(int(drama_id))
        self.render("episode_play.html", ep = episodes[int(ep)])

class IndexHandler(BaseHandler):
    def get(self):
        self.redirect("/drama/list")


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
