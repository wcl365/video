# coding: utf8

import requests
import re
# import mechanize, cookielib
# from selenium import webdriver
import json

FAKE_HEADER = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
}


class BaseParser(object):

    def __init__(self):
        pass
        # self.br = mechanize.Browser()
        # self.br.addheaders = [("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4")]
        # cj = cookielib.LWPCookieJar()
        # self.br.set_handle_equiv(True)
        # self.br.set_handle_gzip(True)
        # self.br.set_handle_redirect(True)
        # self.br.set_handle_referer(True)
        #
        # self.br.set_debug_http(True)
        # self.br.set_debug_redirects(True)
        # self.br.set_debug_responses(True)
        # self.br.set_cookiejar(cj)

    def r1(self, pattern, text):
        m = re.search(pattern, text)
        if m:
            return m.group(1)

    def get_decoded_html(self, url):
        response = requests.get(url, headers=FAKE_HEADER)
        if response.status_code != 200:
            return None
        data = response.content
        charset = self.r1(r'charset=([\w-]+)', response.headers['content-type'])
        if charset:
            return data.decode(charset)
        else:
            return data

    def get_decoded_json(self, url):
        data = self.get_decoded_html(url)
        if data:
            return json.loads(data)
