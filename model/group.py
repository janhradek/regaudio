import sqlalchemy
import sqlalchemy.orm

from .base import Base

class Group(Base):
    '''
    A group of tracks: an album, compilation, a mix
    '''
    __tablename__ = "groups"

    idno = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    fav = sqlalchemy.Column(sqlalchemy.Boolean)
    grouptracks = sqlalchemy.orm.relationship("GroupTrack", backref="group", cascade="all, delete, delete-orphan")

    CaptionAllTracks = "All tracks (no group)"
    CaptionFavPrefix = "* "
    CaptionFavSuffix = " [FAVORITE]"

    def __init__(self, name):
        self.name = name

    def menucaption(self):
        if self.fav:
            return self.CaptionFavPrefix + self.name + self.CaptionFavSuffix
        return self.name

    @staticmethod
    def namefromcaption(caption):
        # * xyz [FAVORITE] -> xyz
        if caption.startswith(Group.CaptionFavPrefix) and caption.endswith(Group.CaptionFavSuffix):
            return caption[len(Group.CaptionFavPrefix):len(caption) - len(Group.CaptionFavSuffix)]
        # All tracks (no group) -> None
        if caption == Group.CaptionAllTracks:
            return ""
        return caption

