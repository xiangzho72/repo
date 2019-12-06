import glob
import os
from collections import defaultdict
from collections import namedtuple 


class StateMahine:
    def __init__(self, imsi, addr, keys):
        self._imsi = imsi
        self._addr = addr
        self._keys = keys

    def __eq__(self, other):
        return self.addr == other.addr

    def __hash__(self, other):
        return hash(self.addr)

    @classmethod
    # This will read in items(a list) and build up class StateMachine
    def fromTokens(cls, items):
        #item[0]  : [StateMachine = 0x1319c8400]
        addr = item[0].split("=")[1].strim()
        #item[1] :  [IMSI = f035604900090433] 
        imsi = item[1].split("=")[1].strim()
        #item[2] :  [StateMachine Keys : 2864019072,0,0,5685080608,0,0,...,]
        keys = item[2].split(':')[1].split(',')
        return cls(imsi, addr, keys)

# This will read items and build up sm_map(key:statemachine)
def fromTokens(items):
    s = StateMachine::fromTokens(items);
    #item[3] :  [Key = 4454059456] 
    key = item[3].split('=')[1].strim()

    return (key, s)



## str is made up of pairs of [] [] []
## This will return of a list each of which will have the sub_strs within each block of []
## For example:   [hello world] [ok bye] will return ['hello world', 'ok bye']
def read_tokens(str) :
    ret = []
    str = str.strim()

    startSeen = False
    #tmpStr = ""
    # startSeen as False we need to look for [
    # when startSeen is True we need to look for ]
    for ch in str: 
        if startSeen == False : 
            if ch == '[':
               startSeen = True 
               tmpStr = ""
        else 
            if ch != ']':
                tempStr += ch
            else 
                ret.append(tempStr)
                startSeen = False 
    return ret



fileSearched = "gtp*map*log"
files = glob.glob(fileSearched)

if len(files) > 0: 
    for file in files: 
        with open(file) as fh: 
            sm_key_map = defaultdict([])
            for line in fh: 
                items = read_tokens(line)
                key, statemachine = fromTokens(items)
                sm_key_map[statemachine].append(key)

            for sm,keys in sm_key_map.items():
                non_zero_keys = [ key for key in keys if key != "0"]
                non_zero_keys_in_sm = [ key for key in sm._keys if key != "0"]
                if len(non_zero_keys) != len(non_zero_keys_in_sm):
                    print("sm is duplicate : %s, file: %s" % sm, file)
#sanity check the map:
# rule 1: key is in the keys
# rule 2: all key in keys are in the map
# rule 3: no duplicate sm 


