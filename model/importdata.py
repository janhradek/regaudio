import xml.sax.handler
import glob
import os.path
import re

from model.track import Track
from model.group import Group
from model.grouptrack import GroupTrack
from model.model import TrackModel
import model.tracktime
from var.utils import filenametoinfo
from model.config import CFG, cfgvaltolistlist

class ImportEntry(object):
    
    MAXCANDIDATES = 25

    headers = ["Search key", "Found", "Selected", "No", "Artist", "Name", "New", "Rating", "From", "Length"]
    
    def __init__(self):
        self.originalkey = ""
        self.searchkey = ""
        self.tracks = None
        self.track = None
        self.best = None
        self.no = 0
        self.nobackup = 0
        self.artist = ""
        self.artistbackup = ""
        self.name = ""
        self.namebackup = ""
        self.new = True
        self.rating = 0
        self.fromms = 0
        self.lengthms = 0
        
    def bycol(self, col, newvalue=None, edit=False):
        # self.searchkey
        if col == 0:
            if newvalue != None:
                self.searchkey = newvalue
                return True
            return self.searchkey
        # found / tracks
        elif col == 1:
            if newvalue != None:
                raise Exception("The found tracks are changed through Search key")
            if not self.tracks:
                return ""
            else:
                if self.best[0]:
                    return str(len(self.tracks)) + "  " + self.best[0].strip()
                return len(self.tracks)
        # selected / new
        elif col == 2:
            if newvalue != None:
                raise Exception("Pick a track from the context menu")
            if self.track == True:
                return "***" # this indicates a new track
            elif self.track != None:
                return "sel"
            return ""   
        # no         
        elif col == 3:
            if newvalue != None:
                self.no = newvalue
                return True
            return self.no
        # artist
        elif col == 4:
            if newvalue != None:
                self.artist = newvalue
                return True
            return self.artist
        # name
        elif col == 5:
            if newvalue != None:
                self.name = newvalue
                return True 
            return self.name
        # new
        elif col == 6:
            if newvalue != None:
                self.new = newvalue
                return True 
            return self.new
        # rating
        elif col == 7:
            if newvalue != None:
                self.rating = newvalue
                return True 
            return self.rating
        # froms        
        elif col == 8:
            if newvalue != None:
                nw, ok = model.tracktime.strtototal(newvalue)
                if ok: self.fromms = nw
                return ok                            
            return model.tracktime.totaltostr(self.fromms, edit)
        # lengthms
        elif col == 9:
            if newvalue != None:                
                nw, ok = model.tracktime.strtototal(newvalue)
                if ok: self.lengthms = nw
                return ok       
            return model.tracktime.totaltostr(self.lengthms, edit)            

    def tipbycol(self, col):
        if col == 0: # "Search key"
            sk = TrackModel.removeissues(self.searchkey)
            skb = TrackModel.removeissues(self.originalkey)
            res = "(" + sk + ")"
            if sk != skb:
                res = self.originalkey + "\n" + res
            return res
        elif col == 1: #  "Found"
            return "\n".join(tt.menucaption(self) for tt in self.tracks).strip()
        elif col == 2: # "Selected", 
            return "New" if self.track == True else "Selected" if self.track != None else None
        elif col == 3: # "No"
            if self.no != self.nobackup:
                return str(self.nobackup)
        elif col == 4: # "Artist"
            res = ""
            if self.artistbackup.strip() != self.artist.strip():
                res = self.artistbackup + "\n"
            if (self.track != None and self.track != True 
                and self.track.artist.strip().lower() != self.artist.strip().lower()):
                res += "(" + self.track.artist + ")"
            return res.strip()
        elif col == 5: # "Name"
            res = ""
            if self.namebackup.strip() != self.name.strip():
                res = self.namebackup + "\n"
            if (self.track != None and self.track != True 
                    and self.track.name.strip().lower() != self.name.strip().lower()):
                res += "(" + self.track.name + ")"
            return res.strip()
        elif col == 6: # "New"
            res = "New" if self.new else "Old"
            if self.track != None and self.track != True and self.track.new != self.new:
                res += " (" + self.track.new + ")"
            return res
        elif col == 7: # "Rating"
            return str(self.rating)
            if self.track != None and self.track != True and self.track.rating != self.rating:
                res += " (" + self.track.rating + ")"
            return res
        elif col == 8: # "From"
            pass
        elif col == 9: # "Length"
            pass
        return None

    @staticmethod    
    def isStar(col):
        return (col == 7)

    @staticmethod    
    def isCheck(col):
        return (col == 6)
    
    def createTrack(self):
        return Track(self.artist, self.name, self.new, self.rating)
    
    def createGroupTrack(self):
        return GroupTrack(self.no, self.fromms, self.lengthms)
            
    def applyToTrack(self):
        if not type(self.track) is Track:
            return

        self.track.artist = self.artist
        self.track.name = self.name
        self.track.new = self.new
        self.track.rating = self.rating

    def unwindsearchkey(self, dry=False):#, row):
        '''
        turn current searchkey to artist and name (if possible)
        '''
        # the searchkey is always in the form !a:something !n:something
        artist = name = "" # values to be set to entry
        last = "" # what was last        
        data = ""
        #ee = self.lst[row] # the ImportEntry
        for ss in self.searchkey.split("!"):            
            ss = ss.strip()
            if ss.startswith("a:"):
                last = "a"
                data = ss[2:]
            elif ss.startswith("n:"):
                last = "n"
                data = ss[2:]
            else:
                data = "!" + ss
            
            if last == "a":
                artist += data
            elif last == "n":
                name += data
            # other values are ignored
        
        if artist != "" and name != "" and not dry:
            self.artist = artist
            self.name = name
        return artist, name

    def applysearchkey(self, model):
        sk = self.searchkey.lower()
        self.tracks = model.tracks.filter(sk, self.__class__.MAXCANDIDATES )
        self.track = None                
        self.best = ["", None]

        # determine best matching track (if any)
        order = ["** ", "+* ", "*+ ", "++ ", "_* ", "_+ ", "*_ ", "+_ ", ""]
        rank = len(order) - 1 # the worst is the best by default
        if self.tracks:
            for tt in self.tracks:
                # will raise ValueError if we forget to update order in the future
                ii = order.index(tt.match(self))
                if ii < 0 or ii >= rank:
                    continue
                rank = ii
                self.best = [order[rank], tt]
                if rank == 0:
                    break

    def selecttrack(self, track):
        self.track = track
        if self.track != True: # if it is actually a track
            self.artist = track.artist
            self.name = track.name
            self.rating = track.rating
            self.new = track.new        

    @staticmethod
    def coltype(col):
        '''
        returns something if other values depends on it - a tuple of string and list
        
        return what changed and what will depend (index) on it, to pass it to the qt
        '''
        if col == 0:
            return "sk", [1, 2]
        return "", None
        
    @staticmethod    
    def editable(col):
        if col == 1 or col == 2:
            return False
        return True                

class ImportData(object):

    nameremove = cfgvaltolistlist(CFG["regaudio"]["import name remove"], extend=True)
    
    def __init__(self, model, name=""):        
        self.model = model
        self.lst = None
        if type(name) is list:
            name = name[0]
        self.name = self.namebackup = name
        self.fav = True

        # just make sure the following function is properly initialized first
        # TODO it would be better to create a class or singleton 
        filenametoinfo("", CFG["regaudio"]["import filename exceptions"])
        
    def rowCount(self):
        return len(self.lst)  

    def headerCount(self):
        return len(ImportEntry.headers)

    def header(self, col):
        return ImportEntry.headers[col]        

    def isStar(self, col):
        return ImportEntry.isStar(col)

    def isCheck(self, col):
        return ImportEntry.isCheck(col)

    def readdatapre(self, what, file):
        """
        reading data pre check
 
        returns tuple (what suggestion, question to ask)
        returns None, None if everything seems to be ok
        """
        if what == "dir" and DirReader.hascues(file):
            return "cue", \
                "It seems that the directory has .cue files. Do you wish to import these instead?"
        return None, None
        
    def readdata(self, what, filenames):
        if what == "mm":
            p = xml.sax.make_parser()
            h = MMHandler()
            p.setContentHandler(h)
            p.parse(filenames)
            self.lst = h.lst
            self.mmTranslateSearchKey()
        elif what == "cue":
            cr = CueReader(filenames)
            self.lst = cr.makelist()
        elif what == "dir":
            dr = DirReader(filenames)
            self.lst = dr.makelist()
        for ee in self.lst:
            ee.originalkey = ee.searchkey 
            ee.unwindsearchkey()
            ee.artistbackup = ee.artist 
            ee.namebackup = ee.name 
            ee.nobackup = ee.no 
            ee.applysearchkey(self.model)

    def insertrows(self, position, rows):
        if self.lst == None:
            self.lst = []
            
        for row in range(position, position+rows):            
            ne = ImportEntry()
            self.lst.insert(row, ne)            
        
    def removerows(self, position, rows):            
        '''
        remove rows given by starting position and number of rows
        '''
        if self.lst == None:
            return None

        for row in range(position+rows-1, position-1, -1):
            del(self.lst[row])                             

    def getcleanname(self, cutleft='/', removechars='-_.'):
        """cleanup the name by either cuting the prefix given by the last char and/or removing some chars"""
        name = self.name
        CUTCHAR = '/'
        if cutleft and CUTCHAR in name:
            name = name[name.rfind(CUTCHAR)+1:]
        if removechars:
            tr = str.maketrans(removechars, " "*len(removechars))
            name = name.translate(tr)
        name = name.strip()
        return name

    def checknamedup(self, name=None):
        if not name:
            name = self.name
        return self.model.getGroups().groupexists(name)
        
    def store(self, stats):
        '''
        store every item in the list according to the data in it
        this might create a group, grouptracks and tracks
        '''        
        ss = self.model.getSession()
        
        gg = None
        if not self.name is None and self.name.strip() != "":
            gg = Group(self.name)
            gg.fav = self.fav
            ss.add(gg)            
            ss.merge(gg) # merge the idno
            
        for ee in self.lst:
            tt = None            
            if ee.track == True:
                tt = ee.createTrack()
                ss.add(tt)
                stats.inctotal()

            elif ee.track != None:
                ee.applyToTrack()
                tt = ee.track
                
            if tt != None and gg != None:
                gt = ee.createGroupTrack()
                ss.add(gt)
                gt.track = tt                
                gg.grouptracks.append(gt)
                
        ss.commit()

        if gg:
            return gg.idno
        return None
        
    def editable(self, col):
        return ImportEntry.editable(col)
    
    def data(self, row, column, edit=False):
        return self.lst[row].bycol(column, edit=edit)

    def tip(self, row, col):
        return self.lst[row].tipbycol(col)
    
    def setdata(self, row, column, value):
        '''
        return a list of columns to update
        '''        
        ee = self.lst[row]
        ok = ee.bycol(column, value)
        
        # sk -> fetch tracks, clear picked, 
        ct, cols = ImportEntry.coltype(column)
        if ct == "sk":
            ee.applysearchkey(self.model)
            
        return cols, ok    
    
    def reset(self, row):              
        ee = self.lst[row]
        ee.searchkey = ee.originalkey
        ee.no = ee.nobackup
        ee.unwindsearchkey()
        ee.applysearchkey(self.model)

    def sanitizeArtistName(self, row):
        ee = self.lst[row]
        # currently only name is being sanitized
        # removed items will be replaced with a space
        for rr in self.__class__.nameremove:
            rr = rr.lower() 
            if rr == rr.upper(): 
                # simple replacement is sufficient
                ee.name = ee.name.replace(rr, " ")
                continue
            # case insensitive search and replace
            while True:
                nn = ee.name.lower()
                ii = nn.find(rr)
                if ii == -1:
                    break
                ee.name = " ".join((ee.name[:ii].strip(), ee.name[ii+len(rr):].strip()))
        
    def searchToArtistName(self, row):
        self.lst[row].unwindsearchkey()
        
    def artistNameToSearch(self, row):
        ee = self.lst[row]
        ee.searchkey = "!a:" + ee.artist + " !n:" + ee.name        
        ee.applysearchkey(self.model)

    def artistToSearch(self, row):
        ee = self.lst[row]
        ee.searchkey = "!a:" + ee.artist
        ee.applysearchkey(self.model)

    def nameToSearch(self, row):
        ee = self.lst[row]
        ee.searchkey = "!n:" + ee.name        
        ee.applysearchkey(self.model)

    def nameCutToSearch(self, row):
        ee = self.lst[row]
        nn = ee.name
        nn, sep, tail = nn.partition("[")
        nn, sep, tail = nn.partition("(")
        ee.searchkey = "!n:" + nn.strip()
        ee.applysearchkey(self.model)
        
    def rating(self, row, rr):
        ee = self.lst[row]
        ee.rating = rr

    def toggleNewFlag(self, row, value=None):
        ee = self.lst[row]
        if value == None:
            ee.new = not ee.new
        else:
            ee.new = value

    def sanitizeTrackNo(self):
        # determine the case
        if self.lst[0].no == "" or self.lst[0].no == 0 or self.lst[0] == None:
            # no track numbers at all
            for ii, ie in enumerate(self.lst):
                ie.no = ii + 1
        else:
            prev = int(self.lst[0].no) - 1
            cd = 1
            for ie in self.lst:
                pp = prev
                prev = int(ie.no)
                if int(ie.no) - 1 != pp:
                    cd = cd + 1
                ie.no = (cd * 100) + int(ie.no)
    
    def mmTranslateSearchKey(self):
        '''
        turn the serchkeys in plaintext to advanced filters, (from Freemind mindmaps)
        '''       
        for ie in self.lst:
            sk = ie.searchkey
            try:                
                ska, skn = sk.split("-")
                sk = "!a:{} !n:{}".format(ska.strip(), skn.strip())
            except ValueError as e:
                pass # keep sk as it is
            ie.searchkey = ie.originalkey = sk

    def getFav(self):
        return self.fav

    def setFav(self, fav):
        self.fav = fav
    
    def getStatus(self):        
        """ total, new, selected, left = self.importdata.getStatistics() """
        total = new = selected = left = 0        
        warnnum = False
        warngroup = False
        dno = {}
        if not self.lst is None:
            for ie in self.lst:
                total += 1                
                if ie.track == None:
                    left += 1
                elif ie.track == True:
                    new += 1
                else:
                    selected += 1
                if not warnnum: # check for duplicate numbers
                    if not ie.no or ie.no in dno:
                        warnnum = True
                    else:
                        dno[ie.no] = None
        if "/" in self.name or len(self.name) > 100:
            warngroup = True

        return (total, new, selected, left, warnnum, warngroup)            

class MMHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.lst = []
        self.entry = None
        
    def startElement(self, name, attrs):
        if name == "node":
            self.entry = ImportEntry()
            self.entry.rating = 5 #1
            self.entry.new = True #False 
            if "TEXT" in attrs:            
                self.entry.searchkey = attrs["TEXT"]
            if "COLOR" in attrs:
                if attrs["COLOR"] == "#996600":
                    self.entry.rating = 2
                    #self.entry.new = True
            self.lst.append(self.entry)
            
        if name == "richcontent":
            print("MMImport: Richcontent not supported")
        
        if name == "icon":
            icn = attrs["BUILTIN"]
            if icn == "button_ok":
                self.entry.rating += 1 #2
            elif icn == "broken-line":
                pass
            elif icn == "full-2":
                self.entry.rating += 0 #2
            elif icn == "full-3":
                self.entry.rating += 0 #3
            elif icn == "messagebox_warning":
                self.entry.rating += 0 #1
            elif icn == "yes":
                self.entry.rating += 0 #1
            else:
                print("MMImport: Unknown icon: {}".format(icn))
                
        if name == "font":
            if "BOLD" in attrs:
                self.entry.rating += 1 #2
    
    def characters(self, content):
        if content.strip() != "":
            print("MMImport: raw data: {}".format(content))
        
    def endElement(self, name):
        if name == "node" and  self.entry != None and self.entry.rating > 10:
            self.entry.rating = 10                            


class CueReader(object):
    
    def __init__(self, fnames):
        self.fnames = fnames
        if not type(self.fnames) is list:
            if os.path.isdir(self.fnames):
                self.fnames = sorted(glob.glob(self.fnames + "/*.cue"))
            else:
                self.fnames = [ self.fnames ]
        self.lst = []
        self.title = ""
        self.performer = ""
        self.file = ""
        self.read()        
        
    def read(self):
        for fn in self.fnames:
            ff = None
            try:
                ff = open(fn, 'r')
                try:
                    lst, fn, perf, title = self.readfile(ff)
                except UnicodeDecodeError as ee:
                    if ff != None:
                        ff.close()

                    # unicode read failed open again in latin1
                    ff = open(fn, 'r',encoding="latin1")
                    lst, fn, perf, title = self.readfile(ff)
                self.lst.extend(lst)
                if fn:
                    self.file = fn
                if perf:
                    self.performer = perf
                if title:
                    self.title = title
            except IOError as ee:
                raise ee 
                #pass #?                                    
            finally:
                if ff != None:
                    ff.close()

    @classmethod
    def readfile(cls, ff):
        lst = []
        fn = None
        perf = None
        title = None

        prev = None # previous track            
        cur = None # current track            
        for line in ff:
            line = line.strip()
            if line.startswith("REM"):
                continue
            if line.startswith("FILE"):
                #self.file = line[5:]                    
                fn = line[5:]                    
            elif line.startswith("TRACK") and line.endswith("AUDIO"):
                prev = cur
                cur = [int(line[6:-6]), "", "", 0, 0] # no, title, perf, start, length
                #self.lst.append(cur)
                lst.append(cur)
            elif line.startswith("PERFORMER"):
                if cur == None:
                    #self.performer = line[10:].strip('"')
                    perf = line[10:].strip('"')
                else:
                    cur[2] = line[10:].strip('"')
            elif line.startswith("TITLE"):
                if cur == None:
                    #self.title = line[6:].strip('"')
                    title = line[6:].strip('"')
                else:
                    cur[1] = line[6:].strip('"')
            elif line.startswith("INDEX 01"):
                if cur == None:
                    continue
                cur[3] = cls.timeframestotime(line[9:])
                if prev != None:
                    prev[4] = cur[3] - prev[3]
        return lst, fn, perf, title 
                
    def makelist(self):
        "list of [no, title , perf, start, length] -> list of ImportEntry"
        lst = []
        for ce in self.lst:
            ie = ImportEntry()
            ie.no = ce[0]
            ie.name = ce[1]
            ie.artist = ce[2]
            ie.fromms = ce[3]
            ie.lengthms = ce[4]
            ie.originalkey = "!a:{} !n:{}".format(ie.artist, ie.name)
            ie.searchkey = ie.originalkey
            lst.append(ie)
        return lst                
                
    @staticmethod
    def timeframestotime(timestr):
        """
        MM:SS:FF -> total MS  (there are 75 frames per second)
        """
        mm, ss, ff = timestr.split(":")
        mm = int(mm)
        ss = int(ss)
        ms = int(int(ff) * 1000 / 75)
                
        return (mm*60 + ss)*1000 + ms
        

class DirReader(object):

    # place res for parsefn here
    
    def __init__(self, dname, handlecue=None):
        self.dname = dname
        self.lst = [] # not the final list, a list of track, artist, name and album

        self.read()

    @staticmethod
    def hascues(dname):
        gcue = glob.glob(os.path.join(dname, "*.cue"))
        if gcue:
            return True
        return False
        
    def read(self):
        # trust m3u files with the order (and, therefore, track numbers)
        # read id3 tags (missing library)
        # read cuesheet if available
        self.lst = []

        if not self.readmp3() and not self.readflac() and not self.readm4a():
            return

        # fix strange track numbers, cleanup names and artists
        for tt in self.lst:
            tt[0] = int(re.sub(r"^\s*(\d*).*$",r"\1", tt[0]))
            tt[1] = tt[1].replace("_", " ")
            tt[2] = tt[2].replace("_", " ")

    def readmp3(self):
        # iglob would not allow the following test if not gmp3
        gmp3 = glob.glob(os.path.join(self.dname, "*.mp3"))
        if not gmp3:
            return False 
        ordered = True # unless stated otherwise
        someordered = False # at least one number somewhere
        from lib.id3reader import Reader
        readervals = ["track", "performer","title"]#, "album"]
        dd = dict() # K: lcase filename V: track info
        for ff in sorted(gmp3):
            # read id3 
            id3 = Reader(ff)
            tt = [ id3.getValue(rv) for rv in readervals ] 
            # check trackno (first index)
            if tt[0] == None or tt[0] == 0 or tt[0].strip() == "" or tt[0] == None:
                # try parsing the filename
                tt = self.mergeid3fn(tt, filenametoinfo(ff))
                if tt[0] == 0 or tt[0].strip() == "" or tt[0] == None:
                    ordered = False
            else:
                someordered = True
            for e,t in enumerate(tt):
                if t == None:
                    tt[e] = ""                

            self.lst.append(tt)
            dd[os.path.basename(ff).strip().lower()] = tt
        if not ordered:
            # means that some tracks lack tracknumber (if not all)
            gm3u = sorted(glob.glob(os.path.join(self.dname, "*.m3u")))
            files = []
            if gm3u:
                # use the order in m3u to assign track no
                if len(gm3u) == 1: 
                    with open(gm3u[0], 'r') as fg: files=fg.readlines()
                else:          
                    readall = False
                    # if the
                    for i, m3u in enumerate(gm3u):
                        if not m3u[0] == chr(i):
                            readall = True
                    if readall: # readthem all then join them together
                        fll = []
                        for m3u in gm3u:
                            with open(m3u, 'r') as fg: 
                                fl = fg.readlines()
                                if not fl in fll: # duplicate m3u happens from time to time
                                    fll.append(fl)
                        for fl in fll:
                            files.extend(fl)
                    else: # just the first one
                        with open(gm3u[0], 'r') as fg: files=fg.readlines()
            else:
                # we could use some magic, but why bother
                # numbers by filename order
                for ii, kk in enumerate(sorted(dd.keys())):
                    dd[kk][0] = str(ii)
        return True

    def readflac(self):
        gflac = glob.glob(os.path.join(self.dname, "*.flac"))
        if not gflac:
            return False 
        for ff in sorted(gflac):
            # no library to read the tags: split by - (track no - artist - name)
            tt = filenametoinfo(ff, stripext=".flac")
            self.lst.append(tt)
        return True

    def readm4a(self):
        gm4a = glob.glob(os.path.join(self.dname, "*.m4a"))
        if not gm4a:
            return False 
        for ff in sorted(gm4a):
            # no library to read the tags: split by - (track no - artist - name)
            tt = filenametoinfo(ff, stripext=".m4a")
            self.lst.append(tt)
        return True

    def mergeid3fn(self, id3, fn):
        """
        merge the two lists in one [trackno, artist, name]

        prefereably use id3 info
        """
        ll = []
        for e, z in enumerate(zip(id3, fn)):
            if e == 3:
                break
            ll.append(z[0] if z[0] != None and z[0].strip() != "" else z[1])
        #ll.append(id3[3]) # album (maybe in the future)
        return ll

    def makelist(self):
        "list of [no, title , perf, start, length] -> list of ImportEntry"
        lst = []
        
        for ce in self.lst:
            ie = ImportEntry()
            ie.no = int(ce[0])
            ie.artist = ce[1]
            ie.name = ce[2]
            ie.fromms = 0
            ie.lengthms = 0
            ie.originalkey = "!a:{} !n:{}".format(ie.artist, ie.name)
            ie.searchkey = ie.originalkey
            lst.append(ie)
        return lst                
