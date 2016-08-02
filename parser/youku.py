# coding: utf8
import requests
import json
import base64
import time
import urllib
import re
from base import BaseParser


class YoukuParser(BaseParser):
    def real_parse(self, vid):
        resp = requests.get('http://v.youku.com/player/getPlayList/VideoIDS/%s/Pf/4/ctype/12/ev/1' % vid)
        meta = json.loads(resp.text)['data'][0]

        self.title = meta['title']
        self.logo = meta['logo']
        ep = meta['ep']
        ip = meta['ip']

        new_ep, sid, token = self._generate_ep(vid, ep)

        m3u8_query = urllib.urlencode(dict(
            ctype=12,
            ep=new_ep,
            ev=1,
            keyframe=1,
            oip=ip,
            sid=sid,
            token=token,
            ts=int(time.time()),
            type='hd2',
            vid=vid,
        ))

        self.hls_url = 'http://pl.youku.com/playlist/m3u8?' + m3u8_query
        self.split_m3u8(self.hls_url)
        print self.urls

    def split_m3u8(self, url):

        data = requests.get(url).text
        data = data.strip();

        lines = data.split("\r\n")
        self.urls = []
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            m = re.match("(http://.*?)\?.*", line)
            if m:
                url = m.group(1)
                if url not in self.urls:
                    self.urls.append(url)

    def _generate_ep(self, vid, ep):
        f_code_1 = 'becaf9be'
        f_code_2 = 'bf7e5f01'

        def trans_e(a, c):
            f = h = 0
            b = list(range(256))
            result = ''
            while h < 256:
                f = (f + b[h] + ord(a[h % len(a)])) % 256
                b[h], b[f] = b[f], b[h]
                h += 1
            q = f = h = 0
            while q < len(c):
                h = (h + 1) % 256
                f = (f + b[h]) % 256
                b[h], b[f] = b[f], b[h]
                if isinstance(c[q], int):
                    result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
                else:
                    result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
                q += 1

            return result

        e_code = trans_e(f_code_1, base64.b64decode(bytes(ep)))
        sid, token = e_code.split('_')
        new_ep = trans_e(f_code_2, '%s_%s_%s' % (sid, vid, token))
        return base64.b64encode(bytes(new_ep)), sid, token
