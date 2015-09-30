# coding: utf8


class _ConfigNoneValueClass(object):
    pass


_ConfigNoneValue = _ConfigNoneValueClass()


class ConfigAware(object):

    def __init__(self, location):
        self.raw_conf = execfile(location)
        if not self.raw_conf:
            raise Exception("load config file error, %s" % location)

    def get(self, key, default=None):
        if not key:
            return None
        parts = key.split(".")
        cur_conf = self.raw_conf
        for part in parts:
            cur_conf = self.raw_conf.get(part, _ConfigNoneValue)
            if cur_conf == _ConfigNoneValue:
                return default
        return cur_conf

    def get_int(self, key, default=None):
        value = self.get(key, default)
        if value is None:
            raise Exception("get int config error, key: %s", key)
        return int(value)
