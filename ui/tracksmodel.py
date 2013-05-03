from PyQt4 import QtCore
from PyQt4 import QtGui

class TracksModel(QtCore.QAbstractTableModel):    
    '''
    An editable ui table model for tracks    
    '''    
        
    # a feedback signal for the window - if new filter rules means that inputs should change
    # this feedback will be used to notify the mainwindow
    feedback = QtCore.pyqtSignal(str, str)
        
    def __init__(self, dbmodel, parent=None):
        super().__init__(parent)
        self.dbmodel = dbmodel
        self.sortingreallyenabled = True
    
    def rowCount(self, parent=None):
        return self.dbmodel.datacount()
        
    def columnCount(self, parent=None):
        return self.dbmodel.headercount()
        
    def headerData(self, section, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self.dbmodel.header(section)
        else:
            return section
        
    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return super().flags(index) | QtCore.Qt.ItemIsEditable
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole: 
            return self.dbmodel.data(index.row(),index.column(), edit= (role == QtCore.Qt.EditRole))
        elif role == QtCore.Qt.ToolTipRole: 
            return self.dbmodel.tip(index.row(),index.column())           
        else:
            return None    
            
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            ok = self.dbmodel.setdata(index.row(),index.column(),value)
            if not ok:
                return False
            self.dataChanged.emit(index,index)
            fb=[("statusupdate","")]
            self.emitfeedback(fb)
            return True
        return False
    
    def insertRows(self, position, rows, index=None):
        if index == None:
            index = QtCore.QModelIndex()
        self.beginInsertRows(QtCore.QModelIndex(), position, position+rows-1)
        self.dbmodel.insertrows(position, rows)
        self.endInsertRows()
        fb=[("statusupdate","")]
        self.emitfeedback(fb)
        return True
    
    def removeRowsList(self, rows):
        '''
        WARNING: this doesn't work as expected, because visually all the rows in the list range are
        deleted, but it may not be true
        '''
        if rows == None or type(rows) != list or len(rows) == 0:
            return
        rows = sorted(rows)
        self.beginRemoveRows(QtCore.QModelIndex(), rows[0], rows[len(rows)-1])
        self.dbmodel.removerowslist(rows)
        self.endRemoveRows()
        fb=[("statusupdate","")]
        self.emitfeedback(fb)
        return True

    def removeRows(self, position, rows, index=None, trackstoo=False):
        '''
        '''
        if index == None:
            index = QtCore.QModelIndex()
        self.beginRemoveRows(QtCore.QModelIndex(), position, position+rows-1)
        self.dbmodel.removerows(position, rows, trackstoo)
        self.endRemoveRows()
        fb=[("statusupdate","")]
        self.emitfeedback(fb)
        return True

    def rating(self, rows, rr):
        if rows == None or type(rows) != list or len(rows) == 0:
            return
        #self.beginResetModel()
        self.dbmodel.rating(rows, rr)
        self.layoutChanged.emit()
        #self.endResetModel()        
        fb=[("statusupdate","")]
        self.emitfeedback(fb)

    def toggleNew(self, rows):
        if rows == None or type(rows) != list or len(rows) == 0:
            return
        #self.beginResetModel()
        self.dbmodel.toggleNew(rows)
        self.layoutChanged.emit()
        #self.endResetModel()        
        fb=[("statusupdate","")]
        self.emitfeedback(fb)
    
    def mergetracks(self, rows, torow):
        '''
        merge all the tracks given by rows into one track given by row
        '''
        # process the list from the end to keep the row numbers consistent 
        for row in reversed(rows):
            if torow == row:
                continue

            if not self.dbmodel.gtmode:
                self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            torow = self.dbmodel.mergerows(torow, row)
            if not self.dbmodel.gtmode:
                self.endRemoveRows()
        fb=[("statusupdate","")]
        self.emitfeedback(fb)
        return True        
    
    def sort(self, col, order=QtCore.Qt.AscendingOrder):
        '''
        change sorting (keep the rest of the filter)
        '''
        if not self.sortingreallyenabled:
            return
        self.beginResetModel()
        fb = self.dbmodel.setfilter(rule=None, group=None, orderby=col, orderbyasc=(order==QtCore.Qt.AscendingOrder))[1]
        self.endResetModel()        
        fb.append(("resize",""))
        fb.append(("statusupdate",""))
        self.emitfeedback(fb)
    
    def setfilter(self, rule, group="", maxrows=0, page=1):
        '''
        change filter (keep or reset the sort)
        '''
        self.beginResetModel()
        fb = self.dbmodel.setfilter(rule=rule, group=group, maxrows=maxrows, page=page)[1]
        self.endResetModel()        
        fb.append(("resize",""))
        fb.append(("statusupdate",""))
        fb.append(("pagesset",""))
        self.emitfeedback(fb)       

    def detachedcopy(self, row):
        self.dbmodel.detachedcopy(row)
        fb = [("statusupdate","")]
        self.emitfeedback(fb)

    def relink(self, row, tid):
        self.beginResetModel()
        self.dbmodel.relink(row, tid)
        self.endResetModel()
        fb = [("statusupdate","")]
        self.emitfeedback(fb)
                    
    def getSelection(self, selected):
        '''
        return the selected indexes (if valid)
        
        selected is a list of indexes
        '''
        rows = []
        def processIndex(idx):
            if idx != None and idx.isValid() and not idx.row() in rows:
                rows.append(idx.row())
        #processIndex(current)
        if selected == None or len(selected) == 0:
            return rows
        for idx in selected:
            processIndex(idx)
        return sorted(rows)

    def emitfeedback(self, fb):
        '''
        sends feedback data (ui changes) to main window through connected signal
        '''
        for m, v in fb:
            self.feedback.emit(m, str(v))        

    def isStar(self, index):
        return self.dbmodel.isStar(index.column())

    def isCheck(self, index):
        return self.dbmodel.isCheck(index.column())
