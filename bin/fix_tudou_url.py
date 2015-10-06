
import re
from model.models import dramaEpisodeModel, dramaModel

def fix():
    dramas = dramaModel.list_avalable(200, 0)
    for d in dramas:
        eps = dramaEpisodeModel.get_by_drama_id(d['id'])
        if not eps[0]['hd_url'].startswith("http://vr.tudou.com/v2proxy"):
            continue
        for ep in eps:
            url, hd_url = ep['url'], ep['hd_url']
            url, hd_url = change_url(url), change_url(hd_url)
            dramaEpisodeModel.update_url(ep['id'], url, hd_url)

def change_url(url):
    m = re.search("it=(\d+)", url)
    iid = m.group(1)
    m = re.search("st=(\d+)", url)
    st = m.group(1)
    return 'http://vr.tudou.com/v2proxy/v2.m3u8?it=%s&st=%s' % (iid, st)

if __name__ == '__main__':
    fix()
