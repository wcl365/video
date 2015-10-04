# -*- coding: utf-8 -*-

__all__ = ['WechatBasic', 'WechatExt']

try:
    from wechat.basic import WechatBasic
    from wechat.ext import WechatExt
except ImportError:
    pass
