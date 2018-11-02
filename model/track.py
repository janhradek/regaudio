import sqlalchemy
import sqlalchemy.orm

from .base import Base
from .group import Group

class Track(Base):
    '''
    This class represents a single track (and a row in table TRACKS)
    '''

    __tablename__ = "tracks"

    idno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    #idno = sqlalchemy.Column(sqlalchemy.Integer, Sequence('user_id_seq'), primary_key=True)
    artist = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    new = sqlalchemy.Column(sqlalchemy.Boolean)
    rating = sqlalchemy.Column(sqlalchemy.Integer)

    grouptracks = sqlalchemy.orm.relationship("GroupTrack", backref="track", cascade="all, delete, delete-orphan")

    headers = ["Artist", "Name", "New", "Rating"]

    def __init__(self, artist, name, new, rating):
        self.artist, self.name, self.new, self.rating = artist, name, new, rating

    def copy(self):
        return Track(self.artist, self.name, self.new, self.rating)

    def menucaption(self, mark=None):
        """ return a string that nicely represents the track """
        mark = self.match(mark)

        #return "{}{} - {}{}   R:{}".format(mark, self.artist, self.name,
        #        "   [NEW]" if self.new else "", self.rating)
        return "{}{} - {}{}   [{}]".format(mark, self.artist, self.name,
                "   [NEW]" if self.new else "", self.nicerating())

    def nicerating(self):
        """ output rating as a set of stars (string) 3.5 (r:7) -> **+-- """
        nice = "*" * int(self.rating / 2)
        if self.rating % 2:
            nice += "+"
        nice += "-" * (5-len(nice))
        return nice

    def match(self, target):
        """ return a string indicating how much the artist and name matches against the given mark
        mark can be a track or importentry
        """
        if target == None:
            return ""

        if target.artist.lower().strip() == self.artist.lower().strip():
            mm = "*"
        else:
            mm = "_"

        if target.name.lower().strip() == self.name.lower().strip():
            mm += "* "
        else:
            mm += "_ "

        from .model import TrackModel
        if mm[0] != "*":
            if (TrackModel.removeissues(self.artist).strip()
                == TrackModel.removeissues(target.artist).strip()):
                mm = "+" + mm[1:]
        if mm[1] != "*":
            if (TrackModel.removeissues(self.name).strip()
                == TrackModel.removeissues(target.name).strip()):
                mm = mm[0] + "+ "
        #else:
        #    print("..", TrackModel.removeissues(self.artist + self.name))
        #    print("  ", TrackModel.removeissues(target.artist + target.name))
        if mm == "__ ":
            mm = ""

        return mm

    def bycol(self, col, newvalue=None, edit=False):
        '''
        get/set column newvalue by column number (according to headers)

        if newvalue is not provided (or None) the value will not be set
        if newvalue == None the current value is returned, otherwise True is returned to confirm success
        '''
        if col == 0:
            if newvalue != None:
                self.artist = newvalue
                return True
            return self.artist
        elif col == 1:
            if newvalue != None:
                self.name = newvalue
                return True
            return self.name
        elif col == 2:
            if newvalue != None:
                self.new = newvalue
                return True
            return self.new
        elif col == 3:
            if newvalue != None:
                self.rating = newvalue
                return True
            return self.rating

        return None

    def tipbycol(self, col):
        if col == 2:
            return "New" if self.new else "Old"
        elif col == 3:
            return str(self.rating)
        return None

    @staticmethod
    def isStar(col):
        return (col == 3)

    @staticmethod
    def isCheck(col):
        return (col == 2)

    @staticmethod
    def colbycol(col):
        '''
        return sqlalchemy column by column number (according to headers)
        '''
        if col == 0:
            return Track.artist
        elif col == 1:
            return Track.name
        elif col == 2:
            return Track.new
        elif col == 3:
            return Track.rating
        return None
