from pyquery import PyQuery as pq
import requests
import re

from model.models import dramaModel, DramaEpisodeModel, UrlContentModel
from parser.tudou import TudouParser, BaseParser
from common import env
env.loadEnv()

HOST = "http://www.hanjucc.com"

class DramaSource(BaseParser):
    URL = [
            "http://www.hanjucc.com/hanju/list_140_1.html",
            "http://www.hanjucc.com/hanju/list_140_2.html",
            "http://www.hanjucc.com/hanju/list_140_3.html",
            "http://www.hanjucc.com/hanju/list_140_4.html"
        ]

    def __init__(self):
        self.dramaEpisodeSource = DramaEpisodeSource()

    def fetch(self):
        for url in self.URL:
            self._fetch(url, 2015)

    def _fetch(self, url, year):
        text_content = self.get_decoded_html(url)
        print text_content
        content = pq(text_content)
        trs = content("#tg_box_con li")
        for tr in trs:
            tr = pq(tr)
            pic = HOST + tr("a img").attr("src")
            href = HOST + tr("a").attr("href")
            name = tr(".jd_info .tit a b").text()
            name = name.strip()
            if not name:
                print 'fyz error', url
                import pdb; pdb.set_trace()
                continue
            drama = dramaModel.get_by_name(name)
            if not drama:
                actors = tr(".lionhover .right_info .actor").contents()[1]
                desc = tr(".lionhover .right_info .descr").contents()[1]
                print pic, name, year, href, actors, desc
                dramaModel.insert(name, year, pic, actors, desc, href)
                drama = dramaModel.get_by_name(name)
            self.dramaEpisodeSource.fetch(drama['id'], drama['source'])

class DramaEpisodeSource(BaseParser):
    def __init__(self):
        self.tudouParser = TudouParser()
        self.model = DramaEpisodeModel()
        self.urlModel = UrlContentModel()

    def fetch(self, d_id, url, last_ep=0):
        text_content = self.get_decoded_html(url);
        content = pq(text_content)
        trs = content(".abc dt")

        eps = self.model.get_by_drama_id(d_id)
        if eps:
            last_ep = eps[-1]['episode']

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
        text_content = self.get_decoded_html(url)
        if text_content.find("http://www.tudou.com/programs/view") < 0:
            print "not tudou", d_id, url, ep
            return False
        content = pq(text_content)
        tudou_source = content("#ads iframe").attr("src")
        vid = re.search(r"code=(\S+?)&", tudou_source).group(1)

        source = "http://www.tudou.com/programs/view/" + vid
        url, hd_url = self.tudouParser.parse(vid)
        if url and hd_url:
            self.model.insert(d_id, ep, 0, source, url, hd_url)

    def fetch_by_ep_id(self, d_id, vid, cur, last_ep=0):
        for i in range(1, cur+1):
            if i <= last_ep:
                continue
            url = "http://www.hanjucc.com/hanju/%s/%s.html" % (vid, i)
            self.fetch_ep_page(d_id, url, i)

if __name__ == '__main__':
    DramaSource().fetch()


'''
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
'''
