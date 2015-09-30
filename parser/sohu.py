# coding: utf8

from base import BaseParser
import json
import sys
from model.models import dramaModel, dramaEpisodeModel, ucModel, dramaInfoModel
from common import env; env.loadEnv()

class SohuParser(BaseParser):

    def fetch_list(self):
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

    def parse_album_by_aid(self, drama_id, aid, last_ep=0):
        source = "http://api.tv.sohu.com/v4/album/videos/%s.json?page_size=100&api_key=695fe827ffeb7d74260a813025970bd5&plat=3&partner=1&sver=5.0.1&poid=1&page=1&with_fee_video=1&" % aid
        content = self.get_decoded_json(source)
        if not content:
            logging.error("sohu parse album by aid error, %s, %s" % (drama_id, aid))
            return
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
            v1, v2 = ucModel.insert(url), ucModel.insert(hd_url)
            if v1 > 0 and v2 > 0:
                epModel.insert(drama_id, i + 1, 0, source, url, hd_url)
            else:
                logging.error("sohu get url content error, %s, %s" % (url, hd_url))

if __name__ == '__main__':
    SohuDramaListParser().fetch()
