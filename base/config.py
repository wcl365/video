# coding: utf8


class ConfigNoneValue(object):
    pass


_ConfigNoneValue = ConfigNoneValue()


class ConfigAware(object):
    raw_conf = None

    @classmethod
    def init(cls, location):
        cls.raw_conf = execfile(location)
        if not cls.raw_conf:
            raise Exception("load config file error, %s" % location)

    @classmethod
    def get(cls, key, default=None):
        if not key:
            return None
        parts = key.split(".")
        cur_conf = cls.raw_conf
        for part in parts:
            cur_conf = cls.raw_conf.get(part, _ConfigNoneValue)
            if cur_conf == _ConfigNoneValue:
                return default
        return cur_conf

    @classmethod
    def get_int(cls, key, default=None):
        value = cls.get(key, default)
        if value is None:
            raise Exception("get int config error, key: %s", key)
        return int(value)
