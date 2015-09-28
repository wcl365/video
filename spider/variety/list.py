# coding: utf8

import requests
import json
import sys
sys.path.insert(0, "../..")

from model.DBConnector import engine

def gen_url(page, count=20):
    url_tpl = "https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6864&from_mid=1&&format=json&ie=utf-8&oe=utf-8&query=%E7%BB%BC%E8%89%BA%E8%8A%82%E7%9B%AE&sort_key=16&sort_type=1&stat0=&stat1=&stat2=&stat3=&pn="
    return url_tpl + str(count * page) + "&rn=" + str(count)

def store_show(show=None):
    conn = engine.connect();
    conn.execute("insert into variety (name, sort) values (?, ?)", "test", 1)
    conn.close()

def list():

    page = 3
    for i in range(page):
        url = gen_url(i)
        data = json.loads(requests.get(url).text)
        playlist = data['data'][0]['disp_data']

        for show in playlist:
            print show['ename'], show['pic_6n_161'], show['year']
            store_show(show)


store_show()
