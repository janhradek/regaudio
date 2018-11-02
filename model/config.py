import configparser
import os.path
import csv

CFGLOC = "~/.regaudio"
CFGLOC = os.path.expanduser(CFGLOC)

CFG = configparser.ConfigParser()
CFG["regaudio"] = {
    # the location of the database
    "db" : "~/regaudio.sqlite",
    # utils/utils.py, filenametoinfo - works by dashes, this "list" contains exceptions
    "import filename exceptions" : "",
    # stuff to remove (replace by a space) from names in function saniziteArtistName
    "import name remove" : "",
    # strings to ignore during searches, function removeissues
    "search ignore" : "",
    # strings to ignore during searches (spaces replaced with % and prefixed with dtto), function removeissues
    "search ignore magic" : "",
    }

def readcfg():
    global CFG

    if not os.path.exists(CFGLOC) or not os.path.isfile(CFGLOC):
        if not os.path.exists(CFGLOC): # really doesnt exist
            with open(CFGLOC, 'w') as cf:
                CFG.write(cf)
        CFG["regaudio"]["default"] = "True"
    else:
        CFG.read(CFGLOC)
        CFG["regaudio"]["default"] = "False"

    # sanitize value
    CFG["regaudio"]["db"] = os.path.expanduser(CFG["regaudio"]["db"])

def cfgvaltolistlist(val, extend=False):
    """a,b,c \\n d,e,f -> [ [a, b, c] , [d,e,f] ] (extend: [ a,b,c,d,e,f ] )"""
    ll = []
    for cc in val.split("\n"): # by end of lines
        cc = cc.strip()
        llcsv = csv.reader([cc], skipinitialspace=True)
        llcsv = [x for x in llcsv.__next__() if x.strip()] #list(llcsv)[0]
        if not extend:
            ll.append(llcsv)
        else:
            ll.extend(llcsv)
    return ll

readcfg()

