import sys
sys.path.insert(0, ".")

from model.models import DramaModel, DramaEpisodeModel

from spider.drama.get_drama import dramaEpisodeSourceInstance

if __name__ == '__main__':
    dramaModel = DramaModel()
    eModel = DramaEpisodeModel()

    base = int(sys.argv[1])

    ds = dramaModel.list()
    sc = 0
    fc = 0
    for d in ds:
        d_id = d['id']
        if d_id <= base:
            continue
        episodes = eModel.get_by_drama_id(d_id)
        try:
            if not episodes:
                dramaEpisodeSourceInstance.fetch(d_id, d['source'])
            else:
                dramaEpisodeSourceInstance.fetch(d_id, d['source'], episodes[-1]['episode'])
            print 'success', d['id'], d['source']
            sc += 1
        except:
            print 'fail', d['id'], d['source']
            fc += 1

    print sc, fc
