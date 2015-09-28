# coding: utf8

import sys
sys.path.insert(0, '.')
from model.models import DramaGetStrategyModel

strategyModel = DramaGetStrategyModel()

def add_strategy(drama_id, source, strategy):
    strategyModel.insert(drama_id, source, strategy)

if __name__ == '__main__':
    args = sys.argv[1:]
    print args
    drama_id = int(args[0])
    source = args[1].strip()
    s = args[2:]
    strategy = {}
    if len(s) > 0 and len(s) % 2 == 0:
        i = 0
        while i < len(s):
           strategy[s[i].strip()] = s[i+1].strip()
           i += 2
    print drama_id, source, strategy

    add_strategy(drama_id, source, strategy)
