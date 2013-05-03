from PyQt4 import QtCore
from PyQt4 import QtGui

from model import group

class GroupsModel(QtCore.QAbstractListModel):
    '''
    an item model for groups combobox
    
    items are mostly represented as strings (captions)
    '''
    
    # a feedback signal for the window - if new filter rules means that inputs should change
    # this feedback will be used to notify the mainwindow
    feedback = QtCore.pyqtSignal(str, str)            
    
    def __init__(self, dbmodel, parent=None):
        super().__init__(parent)
        self.dbmodel = dbmodel # GroupModel
        
    def rowCount(self, parent=None):
        return len(self.dbmodel.lst)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            g = self.dbmodel.lst[index.row()]
            if g == None:
                return group.Group.CaptionAllTracks
            return g.menucaption()
        elif role == QtCore.Qt.UserRole:
            g = self.dbmodel.lst[index.row()]
            if g == None:
                return group.Group.CaptionAllTracks
            return g.name # id?
        else:
            return None
    
    def favorite(self, row):
        '''
        make/unmake the Group given by the lst index favourite
        returns the new index of the group with list
        return -1 if the index was illegal ie. the index given refered to the "all tracks" group 
        '''
        if not self.dbmodel.canfavorite(row):
            return -1
        self.beginResetModel()
        newrow = self.dbmodel.favorite(row)
        self.endResetModel()
        
        return newrow  
    
    def removeRows(self, position, rows, index=None):
        if index == None:
            index = QtCore.QModelIndex()
        self.beginRemoveRows(QtCore.QModelIndex(), position, position+rows-1)
        self.dbmodel.deletegroups(position, rows)
        self.endRemoveRows()
        return True        
    
    def newGroup(self, name):
        # check the name given
        if self.dbmodel.groupexists(name):
            return -1
        
        self.beginResetModel()
        newrow = self.dbmodel.newgroup(name)
        self.endResetModel()
        
        return newrow
    
    def getGroup(self, idx):
        return self.dbmodel.lst[idx]

    def renameGroup(self, row, newname):
        if self.dbmodel.groupexists(newname):
           return None

        self.beginResetModel() 
        newidx = self.dbmodel.renamegroup(row, newname)
        self.endResetModel() 
        #self.layoutChanged.emit() # this thing causes segv under some circumstances
        return newidx
    
    def setData_disabled(self, index, value, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            if index.row() == 0:
                return False
            if self.data(index, role) == value:
                return True # nothing to do
            if self.dbmodel.groupexists(value):
                return False
            self.beginResetModel() 
            newidx = self.dbmodel.renamegroup(index.row(),value)
            self.endResetModel() 
            self.feedback.emit("group", str(newidx))
            return True
        return False
