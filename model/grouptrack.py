import sqlalchemy

from .base import Base
from .track import Track
import model.tracktime

class GroupTrack(Base):
    '''
    a link between group and track (association pattern)

    backrefs group and track (not listed here)

    To use this first create the group, then group tracks,
    then tracks and add them to grouptracks,
    then add grouptracks to group

    Association Object
    '''

    __tablename__ = "grouptracks"
    idno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    trackid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tracks.idno"))#, primary_key = True)
    groupid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("groups.idno"))#, primary_key = True)
    no = sqlalchemy.Column(sqlalchemy.Integer)
    # time doesnt work well with qt mvc and with python
    fromms = sqlalchemy.Column(sqlalchemy.Integer)
    lengthms = sqlalchemy.Column(sqlalchemy.Integer)

    #track = sqlalchemy.orm.relationship("Track", backref="grouptracks")

    headers = Track.headers[:]
    headers.insert(0, "No")
    headers.append("From")
    headers.append("Length")
    innerheaders = 1 # the track headers start from second index

    def __init__(self, no, froms, lengths):
        self.no = no
        self.fromms = froms
        self.lengthms = lengths

    def bycol(self, col, newvalue=None, edit=False):
        col = GroupTrack.translatecol(col)
        if col < 0:
            return self.track.bycol(-1-col, newvalue, edit)
        if col == 0:
            if newvalue != None:
                self.no = newvalue
                return True
            return self.no
        elif col == 1:
            if newvalue != None:
                nw, ok = model.tracktime.strtototal(newvalue)
                if ok: self.fromms = nw
                return ok
            return model.tracktime.totaltostr(self.fromms, edit)
        elif col == 2:
            if newvalue != None:
                nw, ok = model.tracktime.strtototal(newvalue)
                if ok: self.lengthms = nw
                return ok
            return model.tracktime.totaltostr(self.lengthms, edit)

        return None

    def tipbycol(self, col):
        col = GroupTrack.translatecol(col)
        if col < 0:
            return self.track.tipbycol(-1-col)
        return None

    @classmethod
    def colbycol(cls, col):
        col = cls.translatecol(col)
        if col < 0:
            return Track.colbycol(-1-col)

        if col == 0:
            return cls.no
        elif col == 1:
            return cls.fromms
        elif col == 2:
            return cls.lengthms

    @classmethod
    def isStar(cls,col):
        col = cls.translatecol(col)
        if col < 0:
            return Track.isStar(-1-col)
        else:
            return False

    @classmethod
    def isCheck(cls, col):
        col = cls.translatecol(col)
        if col < 0:
            return Track.isCheck(-1-col)
        else:
            return False

    @classmethod
    def translatecol(cls, col):
        '''
        "translate" the column number to the Track or to local index
        a column in grouptrack (positive) or track (negative - 1)
        '''
        if col >= cls.innerheaders and col < cls.innerheaders + len(Track.headers):
            return cls.innerheaders - col - 1
        elif col >= cls.innerheaders + len(Track.headers):
            return col - len(Track.headers)
        return col

    @classmethod
    def translateorder(cls, direction, col):
        """translate the column number to/from Track
        if direction then translate to track
        return < 0 if the col doesn't have counterpart
        """
        if direction: # gt -> t
            return -1 - cls.translatecol(col)
        else: # t -> gt
            return cls.innerheaders + col
