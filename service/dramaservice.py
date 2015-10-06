# coding: utf8

from model.models import dramaEpisodeModel, dramaModel

class DramaService(object):

    def get_drama_infos(self, count, offset):
        dramas = dramaModel.list_avalable(count, offset)
        for drama in dramas:
            eps = dramaEpisodeModel.get_by_drama_id(drama['id'])
            drama['eps'] = eps
        return dramas

    def search_by_name(self, name, count):
        dramas = dramaModel.search_by_name(name, count)
        for drama in dramas:
            eps = dramaEpisodeModel.get_by_drama_id(drama['id'])
            drama['eps'] = eps
        return dramas

    def new_drama(self, count=10):
        eps = dramaEpisodeModel.new_drama(count=count)
        for ep in eps:
            ep['drama'] = dramaModel.get_by_id(ep['drama_id'])
        return eps
