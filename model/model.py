import os

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql.expression

from model.base import Base
from model.track import Track
from model.group import Group
from model.grouptrack import GroupTrack
from model.stats import Stats

#from .tag import Tag

from model.config import CFG, cfgvaltolistlist

class Model(object):
    def __init__(self, dbfile=None):
        self.session = None
        self.stats = Stats()

        if not dbfile:
            dbfile = CFG["regaudio"]["db"]
        self.engine = sqlalchemy.create_engine('sqlite:///' + dbfile)#, echo=True)
        self.SessionMaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        
        if not os.path.exists(dbfile):
            Base.metadata.create_all(self.engine)
            self.insertExampleData()

        self.tracks = TrackModel(self)
        self.groups = GroupModel(self)
        
    def insertExampleData(self):
        self.getSession()
        g1 = Group("Group 1")
        g2 = Group("Group 2")
        g2.fav = True 
        
        t1 = Track("Bob", "Hello World!", False, 1)
        t2 = Track("Joe", "How are you doing?", True, 3)
        t3 = Track("Jim", "Can't stop dancing", False, 5)
        t4 = Track("Tom", "A simple melody", True, 9)
        
        gt1_1 = GroupTrack(1, 0, 100)
        gt1_1.track = t1
        gt1_2 = GroupTrack(2, 100, 200)
        gt1_2.track = t2
        g1.grouptracks.append(gt1_1)
        g1.grouptracks.append(gt1_2)
        
        gt2_2 = GroupTrack(1, 0, 200)
        gt2_2.track = t2
        gt2_3 = GroupTrack(2, 200, 150)
        gt2_3.track = t3        
        g2.grouptracks.append(gt2_2)
        g2.grouptracks.append(gt2_3)

        self.session.add_all([g1, g2, t1, t2, t3, t4, gt1_1, gt1_2, gt2_2, gt2_3])
        self.session.commit()                
        
    def getTracks(self):
        return self.tracks
    
    def getGroups(self):
        return self.groups    
        
    def getSession(self):
        # always only one session
        if self.session == None:
            self.session = self.SessionMaker()            
        return self.session
    
class GroupModel(object):
    '''
    to be used as lst for groups table
    represents all the groups
    '''
    def __init__(self, model):
        self.model = model
        self.lst = [None] # all the groups, the first being None representin all the tracks
        self.session = None
        self.favs = 0
        
        self.loadgroups()
        
    def _checksession(self):
        if self.session == None:
            self.session = self.model.getSession()            
    
    def loadgroups(self):
        '''
        get all the groups, ordered by favourite and name
        
        the list has one special value at the beginning - None - which resembles the all the tracks
        '''
        self._checksession()
        q = (self.session.query(Group)
                .order_by(sqlalchemy.sql.expression.asc(Group.fav))
                .order_by(Group.name).order_by(Group.idno))
        
        self.lst = q.all()
        if self.lst == None or len(self.lst) == 0:
            self.lst = [None]
        else:
            self.lst.insert(0, None)

        self.resort()
                
    def resort(self):
        '''
        sort the list again        
        '''
        self.favs = 0
        def key(g):
            if g is None:
                return ""
            if g.fav:
                self.favs += 1
                return "    " + g.name.lower()
            return g.name.lower()                         
        self.lst = sorted(self.lst,key=key)
        
    def checkidx(self, idx):
        """True if the index points to a VALID group (ie. not All Tracks)"""
        if idx == 0 or idx >= len(self.lst):
            return False
        return True        
    
    def canfavorite(self, idx):
        return self.checkidx(idx)

    def isfavorite(self, idx):
        if not idx:
            return False
        return lst[idx].fav
    
    def favorite(self, idx):
        '''
        switch favourite on the given group (by idx)
        
        favourite cannot be changed on all the tracks (None)
        changes order immediately
        '''
        
        if not self.checkidx(idx):
            return -1
                
        g = self.lst[idx]
        g.fav = not g.fav        
        idno = g.idno
        
        self._checksession()
        self.session.add(g)
        self.session.commit()
        
        self.resort()
        
        for i in range(len(self.lst)):
            if self.lst[i] != None and self.lst[i].idno == idno:
                return i
                            
        return -1
    
    def deletegroup(self, idx):
        self.deletegroups(idx, 1)
    
    def deletegroups(self, idx, no):
        '''
        remove a serie of groups given as interval index + no 
        
        removing the group doesn't remove the tracks but removes the grouptrack data
        '''
        if not self.checkidx(idx) or not self.checkidx(idx+no-1):
            return False
        
        self._checksession()
        
        while no != 0:        
            g = self.lst[idx]
            if g.fav:        
                self.favs -= 1
            self.session.delete(g)
            del(self.lst[idx])
            no -= 1
         
        self.session.commit()
        return True
        
    def groupexists(self, name):
        self._checksession()
        return (self.session.query(Group).filter(Group.name == name).count() != 0)
    
    def gidToIdx(self, gid):
        '''
        groud id gid to list index
        '''
        i = 0
        for gg in self.lst:            
            if gg != None and gg.idno == gid:
                return i
            i += 1
        return -1
        
    def newgroup(self, name):
        '''
        create a group and insert it to the list in the position
        '''        
        self._checksession()
        
        g = Group(name)
        g.fav = True
        self.lst.append(g)
        self.session.add(g)
        self.session.commit()
        
        self.resort()
        
        return self.lst.index(g)
    
    def renamegroup(self, idx, newname):
        if idx == 0:
            return -1
          
        self._checksession()
        
        g = self.lst[idx]
        g.name = newname
        self.session.add(g)
        self.session.commit()
        
        self.resort()
        
        return self.lst.index(g)

    def getcaptions(self, includeall=False):
        if includeall:
            return [(g.menucaption() if g else Group.CaptionAllTracks) for g in self.lst]
        else:
            return [(g.menucaption()) for g in self.lst if g]
    
class TrackModel(object):
    '''
    to be used as lst for model for tracks table and grouptracks
    
    represents all the tracks or tracks within a group
    '''        
    trtable = str.maketrans(
            " `’~!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?",
            "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    # a list of *verbatim* issues to remove (notably strings with nonalphanumeric characters)
    issues = [x.lower() for x in cfgvaltolistlist(CFG["regaudio"]["search ignore"], extend=True)]
    # a list of magic issues, this is applied after everything nonalphanumeric has been replaced with %
    issuesmagic = cfgvaltolistlist(CFG["regaudio"]["search ignore magic"], extend=True)
    issuesmagic = ["%" + x.strip().lower().replace(" ", "%") + "%" for x in issuesmagic ]

    def __init__(self, model):        
        self.model = model
        self.gtmode = False # True = GroupTracks mode (False = Tracks Only)
        self.group = ""
        self.session = None
        self.lst = None    
        
        # previous values of selections
        self.prevrule = "-1"
        self.prevgroup = "" # was "-1"
        self.prevmax = -1
        self.prevpage = -1
        
        # this is a list containing column indices used for sorting
        # negative values means desc sorting
        # new values are added to the beginning
        # (obsolete:this list is reset if the mode changes from track to grouptracks and vice versa)
        self.ordering = []
        # when gtmode is switched it is sometimes usefull to restore previous ordering
        self.ordbackup = 1

        # it would be better to call setfilter now, but the window isnt working yet 
        # so theres no point doing it yet
        #self.setfilter()

        # statistics
        self.stats = model.stats
        
    def _checksession(self):
        if self.session is None:
            self.session = self.model.getSession()        
    
    def setfilter(self, rule="", group="", maxrows=0, page=1, orderby=None, orderbyasc=True):
        '''
        make a new query by the rule provided, get maxrows results, skip (page - 1)*maxrows results
        default values get an unsorted list of all the tracks (tracks are always sorted by id)
        returns lst list for convenience and a feedback list
        feedback is a list of tuples with name and value
        if rule is None previous value are used except for orderby and orderbyasc
        '''
        self._checksession()
        #print('setfilter(rule="{}", group="{}", maxrows={}, page={}, orderby={}, orderbyasc={})'.format
        #        (rule, group, maxrows, page, orderby, orderbyasc))

        fb = []

        if self.stats.empty():
            self.stats.total = self.session.query(Track).count()
        
        if rule is None and group is None:
            rule = self.prevrule
            group = self.prevgroup
            maxrows = self.prevmax
            page = self.prevpage        
            
        if not type(maxrows) is int:
            maxrows = 0
            fb.append(("max", 0))            
        
        # when group changes, reset page; when mode changes, keep and convert sort order
        newsortcol = None
        if group != self.prevgroup:
            if group == "" or self.prevgroup == "": # mode changed
                newsortcol = self.orderingconvert()
                if newsortcol:
                    fb.append(("sortbycol", newsortcol))
            fb.append(("page", 1))
            page = 1
            
        # if max changes reset page
        if maxrows != self.prevmax:
            fb.append(("page", 1))
            page = 1            
        
        # "register" new orderby
        if orderby != None:
            assert(newsortcol == None)
            # new orderby resets page to 1
            fb.append(("page", 1))
            page = 1
            # shift orderby value to clearly distinguish between asc and desc even for 0
            orderno = orderby + 1
            ordernosign = orderno if orderbyasc else -orderno
            if not self.ordering or self.ordering[-1] != ordernosign:
                self.ordbackup = None
            if orderno in self.ordering:
                self.ordering.remove(orderno)
            elif -orderno in self.ordering:
                self.ordering.remove(-orderno)
            self.ordering.append(ordernosign)
        #print("ordering", self.ordering)
            
        # creating basic query    
        q = None
        if group == "":    
            self.gtmode = False    
            q = self.session.query(Track)
        else:
            self.gtmode = True
            q = self.session.query(GroupTrack).join(Track).join(Group)
            q = q.filter(GroupTrack.groupid==Group.idno).filter(Group.name==group)
                                    
        #rule filter 
        if rule != "":
            q = self.buildquery(q, rule)

        #sorting - remeber the shift between orderby and orderno 
        if self.ordering != None and len(self.ordering) > 0:
            for on in reversed(self.ordering):                
                if on < 0:
                    oby = -1 - on 
                    ofun = sqlalchemy.sql.expression.desc                    
                else:
                    oby = on - 1
                    ofun = sqlalchemy.sql.expression.asc
                if self.gtmode:
                    q = q.order_by(ofun(GroupTrack.colbycol(oby)))
                else:
                    q = q.order_by(ofun(Track.colbycol(oby)))
            
        #by default or as a last rule, sort tracks by trackid, grouptracks by number        
        if self.gtmode:
            q = q.order_by(GroupTrack.no)
        else:
            q = q.order_by(Track.idno)  

        # query is prepared, execute it
        if maxrows == 0:
            self.lst = list(q.all())
        elif maxrows == 1:
            self.lst = q[(page-1*maxrows)]
        else:
            self.lst = q[(page-1)*maxrows:page*maxrows]

        self.stats.newfilter(self.lst, q.count(), q.filter(Track.new == True).count())

        # remember filter for sorting            
        self.prevrule = rule
        self.prevgroup = group
        self.prevmax = maxrows
        self.prevpage = page
            
        # return lst (for convenience) and feedback        
        return self.lst, fb

    def orderingconvert(self):
        """convert ordering between group mode and all tracks mode"""
        # self.prevgroup indicates the previous mode
        newordering = []
        newsortcol = None
        to_track = (self.prevgroup != "")
        for oo in self.ordering:
            # oo is from interval [-inf;-1] [1;inf]
            # it must be converted to column index, sign remebered and then applied afterwards
            sign = oo > 0
            oo = oo - 1 if sign else - 1 - oo
            rr = GroupTrack.translateorder(to_track, oo)
            if rr < 0:
                continue
            #if newsortcol == None: # the first ordering is the most recent
            newsortcol = rr + 1 if sign else - 1 - oo
            newordering.append(newsortcol)
        # backup is currently useful only for grouptracks (switching from track)
        if to_track: # to track - save backup
            self.ordbackup = None
            if not self.ordering:
                self.ordbackup = 1
            elif abs(self.ordering[-1]) == 1:
                self.ordbackup = self.ordering[-1]
        else: # to grouptrack - restore backup
            if self.ordbackup != None:
                newsortcol = self.ordbackup
                newordering.append(newsortcol)
                self.ordbackup = None

        self.ordering = newordering
        return newsortcol

    @classmethod
    def removeissues(cls, rule):
        "replace spaces, non-alphanumeric characters and some keywords with percent signs"
        # FIXME - this is sluggish
        rule = rule.lower().strip()
        rule = rule.replace("!a:", "ARTISTARTISTARTISTARTISTARTISTARTIST")
        rule = rule.replace("!n:", "NAMENAMENAMENAMENAMENAME")
        rule = rule.replace("!r:>", "RATINGMORERATINGMORERATINGMORERATINGMORERATINGMORERATINGMORE")
        rule = rule.replace("!r:<", "RATINGLESSRATINGLESSRATINGLESSRATINGLESSRATINGLESSRATINGLESS")
        rule = rule.replace("!r:", "RATINGRATINGRATINGRATINGRATINGRATING")
        rule = rule.replace("!*:", "NEWNEWNEWNEWNEWNEW")
        rule = rule.replace("!g:", "GROUPGROUPGROUPGROUP")

        for rr in cls.issues:
            rule = rule.replace(rr, "%")
        
        rule = rule.translate(TrackModel.trtable)        

        for rr in cls.issuesmagic:
            rule = rule.replace(rr, "%")
            
        rule = rule.replace("ARTISTARTISTARTISTARTISTARTISTARTIST", "!a:")
        rule = rule.replace("NAMENAMENAMENAMENAMENAME", "!n:")
        rule = rule.replace("RATINGMORERATINGMORERATINGMORERATINGMORERATINGMORERATINGMORE", "!r:>")
        rule = rule.replace("RATINGLESSRATINGLESSRATINGLESSRATINGLESSRATINGLESSRATINGLESS", "!r:<")
        rule = rule.replace("RATINGRATINGRATINGRATINGRATINGRATING", "!r:")
        rule = rule.replace("NEWNEWNEWNEWNEWNEW","!*:")
        rule = rule.replace("GROUPGROUPGROUPGROUP", "!g:")
        
        while "%%" in rule:
            rule = rule.replace("%%", "%")       
            
        # replacement from the future :)
        #import re
        #rep = {"condition1": "", "condition2": "text"} # define desired replacements here
        ## use these three lines to do the replacement
        #rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        #pattern = re.compile("|".join(rep.keys()))
        #text = pattern.sub(lambda m: rep[m.group(0)], text) 

        return rule
    
    def buildquery(self, query, rule):
        """
        convert string rule to sqlaclhemy query

        the rule may ba simple or advanced (!a:artist !n:name !r:rating !*:new)
        """

        q = query # for convenience
        rule = self.removeissues(rule) 
                
        m = ""
        ar = {}        
        for s in rule.split("!"):
            cut = 2
            if s.startswith("a:"):
                m = "artist"
            elif s.startswith("n:"):
                m = "name"
            elif s.startswith("r:<"):
                m = "rating<"
                cut=3
            elif s.startswith("r:>"):
                m = "rating>"
                cut=3
            elif s.startswith("r:"):
                m = "rating"
            elif s.startswith("*:"):
                m = "new"
            elif s.startswith("g:"):
                m = "group"
            else:
                ar[m] = ar.get(m, "") + "!" + s
                continue
            ar[m] = s[cut:].strip()
        # analyze the results a little
        #if not "artist" in ar and not "name" in ar and not "rating" in ar and not "rating>" in ar:
        #    ar = None        
        for rr in ["artist", "name", "rating", "rating>", "rating<", "new", "group"]:
            if rr in ar:
                break
        else: # this is not an advanced rule
            ar = None
        if ar != None and "new" in ar:
            ar["new"] = ( ar["new"].lower() in ["","yes","true","t", "y"] )
        
        commonrule = None
        if ar == None:                
            commonrule = '%'+rule+'%'                
        else:
            if "" in ar and ar[""] != "!":
                commonrule = '%'+ar[""]+'%'
            if "artist" in ar:
                q = q.filter(Track.artist.ilike("%" + ar["artist"] + "%"))
            if "name" in ar:
                q = q.filter(Track.name.ilike("%" + ar["name"] + "%"))
            if "rating" in ar:
                q = q.filter(Track.rating == ar["rating"])
            if "rating<" in ar:
                q = q.filter(Track.rating < ar["rating<"])
            if "rating>" in ar:
                q = q.filter(Track.rating > ar["rating>"])
            if "new" in ar:
                q = q.filter(Track.new == ar["new"])
            if "group" in ar:
                like = "%" + ar["group"].strip() + "%"
                if self.gtmode:
                    # aliases are needed if gtmode
                    ag = sqlalchemy.orm.aliased(Group)
                    agt = sqlalchemy.orm.aliased(GroupTrack)
                    q = q.join(agt, GroupTrack.trackid==Track.idno)
                    q = q.join(ag,  Group.idno==GroupTrack.groupid)
                    q = q.filter(Track.idno == agt.trackid)
                    q = q.filter(agt.groupid == ag.idno)
                    q = q.filter(ag.name.ilike(like))
                else:
                    q = q.join(GroupTrack).join(Group)
                    q = q.filter(GroupTrack.groupid==Group.idno)
                    q = q.filter(Group.name.ilike(like))

        if commonrule:
            q = q.filter(sqlalchemy.or_(Track.artist.ilike(commonrule), Track.name.ilike(commonrule)))
            
        return q
    
    def filter(self, rule, maxt):
        """just query tracks by the given (possibly advanced) rule"""
        self._checksession()
        
        q = self.session.query(Track)
        q = self.buildquery(q, rule)
        q.order_by(Track.artist).order_by(Track.name)
        if not maxt:
            return q.all()
        return q[0:maxt-1]    
    
    def datacount(self):
        """ a safe wrapper around len(self.lst) """
        if self.lst == None:
            return 0
        return len(self.lst)
    
    def data(self, row, col, edit=False):
        '''
        return the entry @ row, col
        '''
        if self.lst == None:
            return None
        if row < 0 or row >= len(self.lst):
            return None
        if self.gtmode:
            if col < 0 or col >= len(GroupTrack.headers):
                return None            
        else:
            if col < 0 or col >= len(Track.headers):
                return None
        return self.lst[row].bycol(col, edit=edit)        

    def tip(self, row, col):
        '''
        return the tooltip @ row, col
        '''
        if self.lst == None:
            return None
        if row < 0 or row >= len(self.lst):
            return None
        if self.gtmode:
            if col < 0 or col >= len(GroupTrack.headers):
                return None            
        else:
            if col < 0 or col >= len(Track.headers):
                return None
        return self.lst[row].tipbycol(col)        
    
    def setdata(self, row, col, value):
        '''
        return the lst @ row, col
        '''
        if self.lst == None:
            return False
        if row < 0 or row >= len(self.lst):
            return False
        if self.gtmode:
            if col < 0 or col >= len(GroupTrack.headers):
                return False            
        else:
            if col < 0 or col >= len(Track.headers):
                return False
        
        t = self.lst[row]
        self.stats.remove(t)
        ok = t.bycol(col, value)
        self.stats.add(t)
        
        # add to session
        self._checksession()
        self.session.add(t)
        if self.gtmode:
            self.session.add(t.track)
        self.session.commit()
        
        return ok
        
    def headercount(self):
        if self.gtmode:
            if GroupTrack.headers is None:
                return 0        
            return len(GroupTrack.headers)              

        if Track.headers is None:
            return 0        
        return len(Track.headers)              
    
    def header(self, col):
        if self.gtmode:
            if col < 0 or col >= len(GroupTrack.headers):
                return None
            return GroupTrack.headers[col]
            
        if col < 0 or col >= len(Track.headers):
            return None
        return Track.headers[col]

    def isStar(self, col):
        if self.gtmode:
            return GroupTrack.isStar(col)
        else:
            return Track.isStar(col)

    def isCheck(self, col):
        if self.gtmode:
            return GroupTrack.isCheck(col)
        else:
            return Track.isCheck(col)
    
    def insertrows(self, position, rows):
        """ only used to create new rows (would work properly for "add to group" imo) """
        if self.lst == None:
            self.lst = []
            
        self._checksession()
        if self.gtmode:
            grp = self.session.query(Group).filter(Group.name==self.prevgroup).one()
            self.session.add(grp)
            for row in range(position, position+rows):            
                nt = Track("","",True,0)
                ngt = GroupTrack(int(row) + 1, 0, 0)
                ngt.track = nt
                grp.grouptracks.append(ngt)
                self.lst.insert(row, ngt)            
                self.stats.add(nt)
                self.session.add(nt)
                self.session.add(ngt)
        else:
            for row in range(position, position+rows):            
                nt = Track("","",True,0)
                self.stats.add(nt)
                self.lst.insert(row, nt)            
                self.session.add(nt)
        self.session.commit()
        
    def removerowslist(self,rows):
        ''' remove the rows given by the list '''
        if self.lst == None:
            return None
        if rows == None or type(rows) != list or len(rows) == 0:
            return None        

        assert() # this method is probably broken
        
        self._checksession()
        for row in reversed(rows):    
            dt = self.lst[row]
            if type(dt) is Track:
                self.stats.remove(dt)
                print("Deleting", dt.menucaption())
            else:
                self.stats.remove(dt, t=False)
            self.session.delete(dt)        
            del(self.lst[row])
        self.session.commit()            
        
    def removerows(self, position, rows, trackstoo):
        '''
        remove rows given by starting position and number of rows
        '''
        if self.lst == None:
            return None
                
        self._checksession()
        for row in range(position+rows-1, position-1, -1):
            dt = self.lst[row]            
            t = True # track will be deleted (not "unlinked")
            if type(dt) is Track:
                print("Deleting", dt.menucaption())
            else: # type(dt) is GroupTrack:
                if trackstoo:
                    print("Deleting", dt.track.menucaption())
                    self.session.delete(dt.track)
                else:
                    t = False
            self.stats.remove(dt, t=t)
            self.session.delete(dt)        
            del(self.lst[row]) 
        self.session.commit()

    def rating(self, rows, rr):
        if self.lst == None:
            return

        for row in rows:
            tt = self.lst[row]
            if self.gtmode:
                tt = tt.track
            self.stats.remove(tt)
            tt.rating = rr 
            self.stats.add(tt)
            self.session.add(tt)
        self.session.commit()

    def toggleNew(self, rows):
        if self.lst == None:
            return

        for row in rows:
            tt = self.lst[row]
            if self.gtmode:
                tt = tt.track
            self.stats.remove(tt)
            tt.new = not tt.new
            self.stats.add(tt)
            self.session.add(tt)
        self.session.commit()
        
    def mergerows(self, torow, row):
        '''
        merge two tracks into one
        
        the track given by row will be deleted, all links to it will be redirected to torow track
        returns the new index of the merged row (which might have changed) 
        '''
        if self.lst == None:
            return -1
        
        #if self.gtmode:
        #    return -1
        
        self._checksession()
        
        tdel = self.lst[row]
        tt = tgt = self.lst[torow]
        if self.gtmode:
            gc = tdel.group
            tt = tt.track
            tdel = tdel.track
        
        # relink grouptracks to the merged track
        # it cant be done directly, because any change to gtdel will also change tdel.grouptracks 
        lgt = []
        for gtdel in tdel.grouptracks:
            lgt.append(gtdel)
        for gtdel in lgt:
            # statrefr - update statistics for this track (remove and add)
            statrefr = self.gtmode and gc == gtdel.group
            if statrefr:
                self.stats.remove(gtdel)
            gtdel.track = tt
            if statrefr:
                self.stats.add(gtdel)
            self.session.add(gtdel)
        
        self.session.delete(tdel)
        if not self.gtmode:
            self.stats.remove(self.lst[row])
            del(self.lst[row])
        else:
            self.stats.total -= 1 # totals have changed, list and group are already updated
        self.session.commit()
        
        return self.lst.index(tgt)
    
    def addtogroup(self, rows, gid, force=False):
        '''
        add tracks given by indices in rows to a group given by gid
        
        do not add the track if the group already contains it        
        '''
        gg = self.session.query(Group).filter(Group.idno == gid).one()
        tids = {}
        lastno = 0 # determine new number for the track
        for gt in gg.grouptracks:
            if gt.no > lastno:
                lastno = gt.no
            tids[gt.track.idno] = None
        lastno += 1
        
        self._checksession()

        addstat = False
        if self.gtmode:
            addstat = (gg == self.lst[0].group)

        # duplicities (and their captions) - tracks that are already in the group
        d = []
        dc = ""
        
        for rr in rows:
            tt = self.lst[rr]
            if self.gtmode:
                tt = tt.track
            if tt.idno in tids and not force:
                d.append(rr)
                dc += "\t" + tt.menucaption() + "\n"
                continue
            gt = GroupTrack(lastno, 0, 0)
            gt.track = tt
            gg.grouptracks.append(gt)
            if addstat:
                self.stats.add(tt,t=False)
            self.session.add(gt)
            lastno += 1
            
        self.session.commit()

        dc = dc.strip()
        return d, dc

    def detachedcopy(self, row):
        """make a copy of the track (through grouptrack) at the given row and relink groutrack to it"""

        # only grouptrack is allowed
        assert(self.gtmode)

        self._checksession()

        gt = self.lst[row]
        tt = gt.track
        tn = tt.copy()
        gt.track = tn

        self.stats.inctotal()

        self.session.add(tn)
        self.session.add(gt)
        self.session.commit()

    def similar(self, row):
        """return a tuple of lists containing identifications and menu captions of tracks similar to the track given by row"""
        assert(self.gtmode)
        self._checksession()

        tor = self.lst[row].track
        sk = tor.name
        # sanitize the searchkey (lowercase, remove everything after first parentheses)
        sk, sep, tail = sk.partition("[")
        sk, sep, tail = sk.partition("(")
        sk = "!n:" + sk.strip()
        tidcap = [] # of tuples of id and captions
        for tt in self.filter(sk, maxt=None):
            tidcap.append((tt.idno, tt.menucaption(tor)))

        return tidcap

    def relink(self, row, tid):
        """replace the track of the grouptrack given by row with the track given by idno tid"""
        # must go through trackmodel (update and stats)
        self._checksession()
        assert(self.gtmode)

        gt = self.lst[row]

        tt = self.session.query(Track).filter(Track.idno == tid).one()

        self.stats.remove(gt)
        gt.track = tt
        self.stats.add(gt)

        self.session.add(gt)
        self.session.commit()
