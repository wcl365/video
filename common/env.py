# coding: utf8

GLOBAL_SIGN = False

def _realLoadEnv():
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    # logging.basicConfig(filename='example.log',level=logging.DEBUG)

    logging.info("loadEnv")

def loadEnv():
    global GLOBAL_SIGN
    if GLOBAL_SIGN:
        return

    _realLoadEnv()
    GLOBAL_SIGN = True
