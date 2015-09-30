# coding: utf8

from model.models import dramaEpisodeModel, dramaModel
from base.context import name, singleton, prototype

class DramaService(object):

    def get_drama_infos(self, count, offset):
        dramas = dramaModel.list_avalable(count, offset)
        for drama in dramas:
            eps = dramaEpisodeModel.get_by_drama_id(drama['id'])
            drama['eps'] = eps
        return dramas
