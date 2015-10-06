# coding: utf8

import requests
from base import BaseParser
import logging
from model.models import ucModel

from common import config
from common import env
env.loadEnv()

class TudouParser(BaseParser):

    def parse(self, vid, store=True):
        content = self.get_decoded_html("http://www.tudou.com/programs/view/%s" % vid)
        if not content:
            return None, None
        r = r'iid:\s?(\d+)'
        iid = self.r1(r, content)

        if iid == None:
            return

        urls = [
            "http://vr.tudou.com/v2proxy/v2.m3u8?it=%s&st=5" % iid,
            "http://vr.tudou.com/v2proxy/v2.m3u8?it=%s&st=3" % iid,
            "http://vr.tudou.com/v2proxy/v2.m3u8?it=%s&st=2" % iid
            ]
        can_urls = []
        for url in urls:
            if store:
                persistentResult = ucModel.insert(url)
            else:
                persistentResult = 1
            if persistentResult >= 0:
                can_urls.append(url)
                if len(can_urls) >= 2:
                    break
        if len(can_urls) == 0:
            logging.info('tudou parse error, cannot get m3u8 content')
            return None, None
        if len(can_urls) == 1:
            return can_urls[0], can_urls[0]
        else:
            return can_urls[1], can_urls[0]


if __name__ == '__main__':
    print TudouParser().parse("38u8BuXqbfw", False)
