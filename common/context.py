# coding: utf8

from functools import wraps

INJECT_KEY_SCOPE = '__inject_scope__'
INJECT_KEY_NAME = '__inject_name__'

SCOPE_SINGLETION = 'singleton'
SCOPE_PROTOTYPE  = 'prototype'

def singleton(f):
    setattr(f, INJECT_KEY_SCOPE, SCOPE_SINGLETION)
    @wraps(f)
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper

def prototype(f):
    setattr(f, INJECT_KEY_SCOPE, SCOPE_PROTOTYPE)
    @wraps(f)
    def wrapper(*args, **kw):
        return f(*args, **kw)
    return wrapper

def name(nm):
    def wrapper(f):
        setattr(f, INJECT_KEY_NAME, nm)
        @wraps(f)
        def inner_wrapper(*args, **kw):
            return f(*args, **kw)
        return inner_wrapper
    return wrapper


class AppContext(object):

    def __init__(self):
        self.ctx = {}

    def getInstance(self, clazz):
        scope = self.getScope(clazz)
        if scope == SCOPE_PROTOTYPE:
            return clazz()

        key = self.getKey(clazz)
        print key
        if self.ctx.has_key(key):
            return self.ctx.get(key)
        else:
            instance = clazz()
            self.ctx[key] = instance
            return instance

    def getKey(self, clazz):
        fullname = clazz.__module__ + "." + clazz.__name__
        anno = getattr(clazz, INJECT_KEY_NAME, None)
        if anno is None:
            return fullname
        else:
            return '%s(%s)' % (fullname, anno)

    def getScope(self, clazz):
        scope = getattr(clazz, INJECT_KEY_SCOPE, None)
        if scope is None:
            return SCOPE_SINGLETION
        return scope
