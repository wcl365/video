# coding: utf8

from base import BaseParser
import json
import sys
sys.path.insert(0, ".")
from model.models import dramaModel, dramaEpisodeModel, ucModel, dramaInfoModel

class SohuDramaListParser(BaseParser):

    def fetch(self):
        url = "http://api.tv.sohu.com/v4/search/channel/sub.json?subId=19&&api_key=695fe827ffeb7d74260a813025970bd5&build=5.0.1.1&offset=0&page_size=100&partner=1&pay_type=0&plat=3&poid=1&sver=5.0.1"
        content = self.get_decoded_html(url)
        content = json.loads(content)
        videos = content['data']['videos']
        sp = SohuParser()
        for v in videos:
            print v['album_name'], v['main_actor'], v['publish_time'][:4], v['aid'], v['hor_w16_pic']
            name = v['album_name']
            d = dramaModel.get_by_name(name)
            if d:
                print 'exist'
                if dramaEpisodeModel.get_by_drama_id(d['id']):
                    continue
                sp.parse_album_by_aid(d['id'], v['aid'])

class SohuParser(BaseParser):

    def __init__(self):
        self.epModel = dramaEpisodeModel
        self.ucModel = ucModel

    def real_url(self, host, prot, file, new):
        url = 'http://%s/?prot=%s&file=%s&new=%s' % (host, prot, file, new)
        start, _, host, key, _, _ = self.get_decoded_html(url).split('|')
        return '%s%s?key=%s' % (start[:-1], new, key)

    def sohu_download(self, vid):
        # vid = self.r1('vid="(\d+)"', self.get_decoded_html(url))
        assert vid
        import json
        data = json.loads(self.get_decoded_html('http://hot.vrs.sohu.com/vrs_flash.action?vid=%s' % vid))
        host = data['allot']
        prot = data['prot']
        urls = []
        data = data['data']
        title = data['tvName']
        size = sum(data['clipsBytes'])
        assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
        for file, new in zip(data['clipsURL'], data['su']):
            urls.append(self.real_url(host, prot, file, new))
        assert data['clipsURL'][0].endswith('.mp4')
        print urls

    def parse_album(self, drama_id, strategy, last_ep=0):
        source = strategy['album_url']
        print source
        content = self.get_decoded_html(source)
        content = json.loads(content)
        videos = content['data']['videos']
        for i, v in enumerate(videos):
            if i+1 <= last_ep:
                continue
            url = v['url_high']
            hd_url = v['url_super']
            print url, hd_url
            self.epModel.insert(drama_id, i + 1, 0, source, url, hd_url)
            self.ucModel.insert(url)
            self.ucModel.insert(hd_url)

    def parse_album_by_aid(self, drama_id, aid, last_ep=0):
        source = "http://api.tv.sohu.com/v4/album/videos/%s.json?page_size=100&api_key=695fe827ffeb7d74260a813025970bd5&plat=3&partner=1&sver=5.0.1&poid=1&page=1&with_fee_video=1&" % aid
        print source
        content = self.get_decoded_html(source)
        content = json.loads(content)
        videos = content['data']['videos']
        for i, v in enumerate(videos):
            if i+1 <= last_ep:
                continue
            if v.get('url_super', None) is not None:
                url = v['url_high']
                hd_url = v['url_super']
            else:
                url = v['url_nor']
                hd_url = v['url_high']
            print url, hd_url
            self.epModel.insert(drama_id, i + 1, 0, source, url, hd_url)
            self.ucModel.insert(url)
            self.ucModel.insert(hd_url)

if __name__ == '__main__':
    SohuDramaListParser().fetch()
