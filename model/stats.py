
from model.grouptrack import GroupTrack

class Stats(object):
    """ manages some basic statistics about the tracks on the current page, the current filter and in total """
    def __init__(self):
        self.total = -1
        self.fltr = -1 # number of tracks in the whole filter (group / all tracks)
        self.fltrnew = -1 # dtto but new tracks only
        self.page = -1 # number of tracks in the current list (current page)
        self.pagenew = -1 # dtto but new tracks only
        # page < fltr and usually (if there are no duplicities) fltr < total
        self.rr = [0] * 11 # ratings count in the current list
        self.statstr = None # cached status string

    def empty(self):
        """ true if the statistics are not yet completely initialized """
        return self.total == -1

    def newfilter(self, lst, group, groupnew):
        """ new filter results """
        self.fltr = group
        self.fltrnew = groupnew

        # reset
        self.page = 0
        self.pagenew = 0
        self.rr = [0] * 11
        self.statstr = None

        for tt in lst:
            self.add(tt, f=False, t=False)

    def inctotal(self, amount=1):
        """increment total by the given amount"""
        self.total += amount
        self.statstr = None

    def add(self, tt, f=True, t=True, amount=1):
        """add track/grouptrack to counters

        f(ilter) and t(otal) means change the respective counters too (on by default)
        set amount to -1 to remove the track from counters (see also remove)
        """
        if type(tt) is GroupTrack:
            tt = tt.track

        assert(abs(amount) == 1)

        self.statstr = None # reset cache

        self.page += amount
        if tt.new:
            self.pagenew += amount
        self.rr[tt.rating] += amount

        if f:
            self.fltr += amount
            if tt.new:
                self.fltrnew += amount
        if t:
            self.total += amount

    def remove(self, tt, f=True, t=True):
        """remove track/grouptrack to counters

        g(roup) and t(otal) means change the respective counters too (on by default)"""
        return self.add(tt, f, t, amount=-1)

    def status(self):
        """return oneline status string"""
        if self.statstr:
            return self.statstr

        avg = 0
        if self.page:
            for r, c in enumerate(self.rr):
                avg += r * c
            avg /= self.page

        ll = lambda x, y: "{}({})".format(x,y) if y else str(x)
        zz = lambda x: x if x else "_"
        rr = [zz(r) for r in self.rr]

        self.statstr = "Page:{}  /  Filter:{}  /  All:{}  Ratings:[{}|{},{},{},{},{}|{},{},{},{},{}]  Average:{:.3}".format(
                ll(self.page, self.pagenew), ll(self.fltr, self.fltrnew), self.total,
                rr[0],rr[1],rr[2],rr[3],rr[4],rr[5],rr[6],rr[7],rr[8],rr[9],rr[10],float(avg))

        return self.statstr
