# coding: utf8

import requests
from base import BaseParser

class TudouParser(BaseParser):

    def parse(self, vid):
        content = self.get_decoded_html("http://www.tudou.com/programs/view/%s" % vid)
        r = r'iid:\s?(\d+)'
        iid = self.r1(r, content)

        if iid == None:
            print 'tudou parse error'
            return

        urls = [
            "http://vr.tudou.com/v2proxy/v2.m3u8?debug=1&it=%s&st=5&pw=" % iid,
            "http://vr.tudou.com/v2proxy/v2.m3u8?debug=1&it=%s&st=3&pw=" % iid,
            "http://vr.tudou.com/v2proxy/v2.m3u8?debug=1&it=%s&st=2&pw=" % iid
            ]
        can_urls = []
        for url in urls:
            c = requests.get(url).content
            if c.find("M3U") > 0:
                can_urls.append(url)
            if len(can_urls) >= 2:
                break
        if len(can_urls) == 0:
            print 'tudou parse error 2'
            return None, None
        if len(can_urls) == 1:
            return can_urls[0], can_urls[0]
        else:
            return can_urls[1], can_urls[0]


if __name__ == '__main__':
    print TudouParser().parse("yWcDTtLvndU")