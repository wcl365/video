from pyquery import PyQuery as pq
import requests
import re

import sys

sys.path.insert(0, "../../")

from model.models import DramaModel, DramaEpisodeModel, UrlContentModel
from parser.tudou import TudouParser, BaseParser

FAKE_HEADER = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
}

HOST = "http://www.hanjucc.com"


class DramaSource(object):
    URL = [
        [
            "http://www.hanjucc.com/hanju/list_140_1.html",
            "http://www.hanjucc.com/hanju/list_140_2.html",
            "http://www.hanjucc.com/hanju/list_140_3.html",
            "http://www.hanjucc.com/hanju/list_140_4.html"
        ],
        [
            "http://www.hanjucc.com/hanju/list_136_1.html",
            "http://www.hanjucc.com/hanju/list_136_2.html",
            "http://www.hanjucc.com/hanju/list_136_3.html",
            "http://www.hanjucc.com/hanju/list_136_4.html"
        ],
        [
            "http://www.hanjucc.com/hanju/list_128_1.html",
            "http://www.hanjucc.com/hanju/list_128_2.html",
            "http://www.hanjucc.com/hanju/list_128_3.html",
            "http://www.hanjucc.com/hanju/list_128_4.html",
        ],
        [
            "http://www.hanjucc.com/hanju/list_125_1.html",
            "http://www.hanjucc.com/hanju/list_125_2.html",
            "http://www.hanjucc.com/hanju/list_125_3.html",
            "http://www.hanjucc.com/hanju/list_125_4.html",
        ],
        [
            "http://www.hanjucc.com/hanju/list_122_1.html",
            "http://www.hanjucc.com/hanju/list_122_2.html",
            "http://www.hanjucc.com/hanju/list_122_3.html",
        ],
        [
            "http://www.hanjucc.com/hanju/list_121_1.html",
            "http://www.hanjucc.com/hanju/list_121_2.html",
            "http://www.hanjucc.com/hanju/list_121_3.html",
        ],
        [
            "http://www.hanjucc.com/hanju/list_120_1.html",
            "http://www.hanjucc.com/hanju/list_120_2.html",
        ],
        [
            "http://www.hanjucc.com/hanju/list_119_1.html",
            "http://www.hanjucc.com/hanju/list_119_2.html",
            "http://www.hanjucc.com/hanju/list_119_3.html",
        ],
        [
            'http://www.hanjucc.com/hanju/list_118_1.html',
            'http://www.hanjucc.com/hanju/list_118_2.html',
            'http://www.hanjucc.com/hanju/list_118_3.html',
        ],
        [
            'http://www.hanjucc.com/hanju/list_117_1.html',
            'http://www.hanjucc.com/hanju/list_117_2.html',
        ],
        [
            'http://www.hanjucc.com/hanju/list_116_1.html',
            'http://www.hanjucc.com/hanju/list_116_2.html',
        ],
        [
            'http://www.hanjucc.com/hanju/list_114_1.html'
        ],
        [
            'http://www.hanjucc.com/hanju/list_113_1.html',
            'http://www.hanjucc.com/hanju/list_113_2.html'
        ]
    ]

    HOST = "http://www.hanjucc.com"

    def __init__(self):
        self.model = DramaModel()

    def fetch(self):
        base = 2015
        i = 0
        for urls in self.URL[0:]:
            for url in urls:
                if base - i == 2003:
                    self._fetch(url, 0)
                else:
                    self._fetch(url, base - i)
            i += 1

    def _fetch(self, url, year):
        text_content = requests.get(url, headers=FAKE_HEADER).content
        text_content = text_content.decode("gb18030")
        content = pq(text_content)
        trs = content("#tg_box_con li")
        for tr in trs:
            tr = pq(tr)
            pic = self.HOST + tr("a img").attr("src")
            href = self.HOST + tr("a").attr("href")
            name = tr(".jd_info .tit a b").text()
            name = name.strip()
            actors = tr(".lionhover .right_info .actor").contents()[1]
            desc = tr(".lionhover .right_info .descr").contents()[1]
            print pic, name, year, href, actors, desc
            self.model.insert(name, year, pic, actors, desc, href)


class DramaEpisodeSource(BaseParser):
    def __init__(self):
        self.tudouParser = TudouParser()
        self.model = DramaEpisodeModel()
        self.urlModel = UrlContentModel()

    def fetch(self, d_id, url, last_ep=0):
        import pdb; pdb.set_trace()
        text_content = self.get_decoded_html(url);
        content = pq(text_content)
        trs = content(".abc dt")

        i = 1
        for tr in trs:
            tr = pq(tr)
            ep_url = HOST + tr("a").attr("href")
            count = tr("a").text()
            ep_group = re.search(r"(\d+)", count)

            if ep_group is not None:
                ep = int(ep_group.group(1))
            else:
                ep = i
            print ep_url, ep
            if ep <= last_ep:
                print "fetch before, skip %s" % ep
                continue
            res = self.fetch_ep_page(d_id, ep_url, ep)
            if res == False:
                break
            i += 1


    def fetch_ep_page(self, d_id, url, ep):
        text_content = requests.get(url, headers=FAKE_HEADER).content
        text_content = text_content.decode("gb18030")
        if text_content.find("http://www.tudou.com/programs/view") < 0:
            print "not tudou", d_id, url, ep
            return False
        content = pq(text_content)
        tudou_source = content("#ads iframe").attr("src")
        vid = re.search(r"code=(\S+?)&", tudou_source).group(1)
        print tudou_source, vid

        source = "http://www.tudou.com/programs/view/" + vid
        try:
            url, hd_url = self.tudouParser.parse(vid)
            if url and hd_url:
                self.model.insert(d_id, ep, 0, source, url, hd_url)
                self.urlModel.insert(url)
                self.urlModel.insert(hd_url)
        except:
            print "get url error", source
            pass


    def fetch_by_ep_id(self, d_id, vid, cur, last_ep=0):
        import pdb; pdb.set_trace()
        for i in range(1, cur+1):
            if i <= last_ep:
                continue
            url = "http://www.hanjucc.com/hanju/%s/%s.html" % (vid, i)
            self.fetch_ep_page(d_id, url, i)

dramaEpisodeSourceInstance = DramaEpisodeSource()
