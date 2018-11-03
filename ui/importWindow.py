from PyQt5 import QtCore, QtGui, QtWidgets

from model.importdata import ImportData
from var import utils
from ui.importWindowUI import Ui_ImportWindowUI
from ui.tracksdelegate import TracksDelegate

class ImportWindow(QtWidgets.QDialog, Ui_ImportWindowUI):

    def __init__(self, importdata, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # setup model (data)
        self.importdata = importdata
        mdl = ImportModel(self.importdata)
        mdl.feedback.connect(self.modelfeedback)
        self.tableimport.setModel(mdl)

        # setup table
        self.tableimport.setItemDelegate(TracksDelegate(mdl))
        self.tableimport.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableimport.customContextMenuRequested.connect(self.trackContextMenuShow)
        self.tableimport.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked |
            QtWidgets.QAbstractItemView.SelectedClicked |
            QtWidgets.QAbstractItemView.EditKeyPressed)
        self.tableimport.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # setup group controls
        self.groupnamecheck(self.importdata.name)
        self.groupnameshow()
        self.groupmenu = QtWidgets.QMenu()
        for act in [
                ["Cleanup name", self.groupnamecleanup],
                ["Edit name", self.groupnamechange],
                ["Restore original name", self.groupnamerestore],
                ]:
            action = QtWidgets.QAction(self)
            action.setText(act[0])
            action.triggered.connect(act[1])
            self.groupmenu.addAction(action)
        self.groupnamechangebtn.setMenu(self.groupmenu)
        self.groupnamechangebtn.clicked.connect(self.groupnamechangebtn.showMenu)

        # setup status line and buttons
        self.okbtn.clicked.connect(self.accept)
        self.cancelbtn.clicked.connect(self.reject)

        self.ignorewarningscb.setChecked(False)
        self.ignorewarningscb.toggled.connect(self.statusSetIgnoreWarnings)
        self.favcb.setChecked(self.importdata.getFav())
        self.favcb.toggled.connect(self.statusSetFavGroup)

        # tracks table context menu
        self.contextMenu = QtWidgets.QMenu()
        self.existingmenu = None
        for act in [
                    ["Select existing", None, "existingmenu", self.trackUpdateExistingMenu], # submenu
                    ["Select the best match", self.trackSelectBest, "B"],
                    ["Quick resolve", self.trackQuickResolve, "Q"],
                    ["Create newtrack", self.trackCreateNew, "C"],
                    [""],
                    ["Rate track", [
                        ["0", lambda : self.trackrating(0), "`"],
                        ["1", lambda : self.trackrating(1), "1"],
                        ["2", lambda : self.trackrating(2), "2"],
                        ["3", lambda : self.trackrating(3), "3"],
                        ["4", lambda : self.trackrating(4), "4"],
                        ["5", lambda : self.trackrating(5), "5"],
                        ["6", lambda : self.trackrating(6), "6"],
                        ["7", lambda : self.trackrating(7), "7"],
                        ["8", lambda : self.trackrating(8), "8"],
                        ["9", lambda : self.trackrating(9), "9"],
                        ["10", lambda : self.trackrating(10), "0"],
                        ]], # submenu
                    ["Toggle new", self.trackToggleNewFlag, "."],
                    [""],
                    ["Add new track", self.trackAdd, "N"],
                    ["Delete track", self.trackDelete],
                    [""],
                    ["Reset all to original", self.trackReset, "R"],
                    ["Sanitize artist and name", self.trackSanitizeArtistName, "S"],
                    ["Sanitize all track numbers", self.trackSanitizeTrackNo],
                    [""],
                    ["Search key to artist and name", self.trackSearchToArtistName, "]"],
                    ["Artist and name to search key", self.trackArtistNameToSearch, "["],
                    ["Artist to search key", self.trackArtistToSearch, ";"],
                    ["Name to search key", self.trackNameToSearch, "'"],
                    ["Name to search key (cut the parenthesis)", self.trackNameCutToSearch, '"'],
                    ]:
            if act[0] == "":
                self.contextMenu.addSeparator()
                continue
            if act[1] == None:
                setattr(self, act[2], QtWidgets.QMenu(self.contextMenu))
                mm = getattr(self, act[2])
                mm.setTitle(act[0])
                mm.aboutToShow.connect(act[3])
                self.contextMenu.addAction(mm.menuAction())
                continue

            alist = None
            tt = None
            if type(act[1]) is list:
                mm = QtWidgets.QMenu(self.contextMenu)
                mm.setTitle(act[0])
                self.contextMenu.addAction(mm.menuAction())
                alist=act[1]
                tt=mm
            else:
                alist=[act]
                tt=self.contextMenu

            for aa in alist:
                action = QtWidgets.QAction(self)
                action.setText(aa[0])
                action.triggered.connect(aa[1])
                if len(aa) == 3:
                    action.setShortcut(QtGui.QKeySequence.fromString(aa[2])) #"Ctrl+"
                tt.addAction(action)
                self.tableimport.addAction(action)
        self.statusUpdate()
        self.tableimport.resizeColumnsToContents()
        self.tableimport.resizeRowsToContents()

    def keyPressEvent(self, e):
        """overriden standard behavior to ignore esc and enter (both would close dialog)"""
        if e.key() == QtCore.Qt.Key_Escape or e.key() == QtCore.Qt.Key_Enter:
            return
        super().keyPressEvent(e)

    def groupnameshow(self):
        """show the groupname, cut it from the left if it is too long (80 chars max)"""
        MAXCHARS=80
        showname = self.importdata.name
        if len(showname) > MAXCHARS:
            self.groupnamelbl.setToolTip(showname)
            showname = "~" + showname[-MAXCHARS+1:]
        else:
            self.groupnamelbl.setToolTip("")
        self.groupnamelbl.setText("Group name: {}".format(showname))

    def groupnamerestore(self):
        """set the groupname to its original"""
        if self.importdata.name == self.importdata.namebackup:
            QtWidgets.QMessageBox.warning(self, "Group name restore",
                    "The group name was not changed.")
            return
        ok = QtWidgets.QMessageBox.question(self, "Group name restore",
                "Restore the original name?\n\n" + self.importdata.namebackup,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if not ok:
            return
        self.importdata.name = self.importdata.namebackup
        self.groupnameshow()
        self.statusUpdate()

    def groupnamecleanup(self):
        # show picker of all the possible choices
        lst = ["Cut from the left to the last '/' and remove some characters",
                "Cut from the left to the last '/'",
                "Remove some characters"]
        sel, ok = QtWidgets.QInputDialog.getItem(self, "Group name cleanup",
                "Select cleanup method",
                lst, current=0, editable=False)
                #flags=0)#QtWidgets.QInputDialog.UseListViewForComboBoxItems)
        if not ok:
            return
        idx = lst.index(sel)
        if idx == 0:
            newname = self.importdata.getcleanname()
        elif idx == 1:
            newname = self.importdata.getcleanname(removechars=None)
        elif idx == 2:
            newname = self.importdata.getcleanname(cutleft=None)
        ok = QtWidgets.QMessageBox.question(self, "Group name cleanup",
                "Is this new name ok?\n\n" + newname,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if not ok:
            return
        self.groupnamecheck(newname)
        self.groupnameshow()
        self.statusUpdate()

    def groupnamechange(self):
        newname, ok = QtWidgets.QInputDialog.getText(self,
                "Group name" # quickfix for the narrow input (below)
                , "New group name: " + " "*100
                , text=self.importdata.name)
        if not ok:
            return

        self.groupnamecheck(newname)
        self.groupnameshow()
        self.statusUpdate()

    def groupnamecheck(self, newname):
        """check for new group name (newname) duplicity against db"""
        origname = self.importdata.name
        while True:
            ok = True
            if not self.importdata.checknamedup(newname):
                break
            newname, ok = QtWidgets.QInputDialog.getText(self, "Group name",
                    "This groupname already exist!\n"
                    "New group name: " + " "*100
                    , text=newname)
            if not ok:
                # restore original name
                newname = self.importdata.name
                # but it can exist too
                ii = 0
                while self.importdata.checknamedup(newname):
                    ii += 1
                    newname = self.importdata.name + " DUP" + str(ii)
                break

        self.importdata.name = newname

    def trackContextMenuShow(self, point):
        point.setX(point.x() + self.tableimport.verticalHeader().width())
        point.setY(point.y() + self.tableimport.horizontalHeader().height())
        self.contextMenu.exec_(self.tableimport.mapToGlobal(point))

    def trackUpdateExistingMenu(self):
        self.existingmenu.clear()

        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        if len(rows) != 1:
            return
        row = rows[0]

        ii = self.importdata.lst[row]
        if ii.tracks == None or len(ii.tracks) == 0:
            return

        for tt in ii.tracks:
            receiver = lambda row=row, track=tt: self.trackSelectExisting(row, track)
            self.existingmenu.addAction(tt.menucaption(ii), receiver)

    def trackSelectExisting(self, row, track):
        ee = self.importdata.lst[row]
        ee.selecttrack(track)

        # FIXME - do this nicer
        self.tableimport.model().layoutChanged.emit()

        self.statusUpdate()

    def trackSelectBest(self):#, row):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        warning = False
        someset = False
        for row in rows:
            ee = self.importdata.lst[row]
            best = ee.best[1]
            if not best:
                warning = True
                continue
            ee.selecttrack(best)
            someset = True

        if someset:
            # FIXME - do this nicer
            self.tableimport.model().layoutChanged.emit()
        if warning:
            QtWidgets.QMessageBox.warning(self, "Warning", "Some tracks have no best matching track!")

        self.statusUpdate()

    def trackQuickResolve(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        someset = False
        for row in rows:
            ee = self.importdata.lst[row]
            mark = ee.best[0]
            best = ee.best[1]
            if not mark in ["** ", "+* ", "*+ ", "++ ", ""]:
                continue
            if mark == "":
                if ee.tracks: # nothing good but some tracks were found
                    continue
                best = True
            ee.selecttrack(best)
            someset = True

        if someset:
            # FIXME - do this nicer
            self.tableimport.model().layoutChanged.emit()

        self.statusUpdate()

    def trackCreateNew(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        warning = False
        someset = False
        for row in rows:
            ee = self.importdata.lst[row]
            if ee.artist == None or ee.artist.strip() == "" or ee.name == None or ee.name.strip() == "":
                warning = True
                continue
            someset = True
            ee.track = True

        if someset:
            # FIXME - do this nicer
            self.tableimport.model().layoutChanged.emit()
        if warning:
            QtWidgets.QMessageBox.warning(self, "Warning", "Some tracks lack artist or name!")

        self.statusUpdate()

    def trackrating(self, rr):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().rating(row, rr)
        self.tableimport.model().layoutChanged.emit()
        self.statusUpdate()

    def trackToggleNewFlag(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().toggleNewFlag(row)
        self.tableimport.model().layoutChanged.emit()
        self.statusUpdate()

    def trackAdd(self):
        tt = self.tableimport
        index = tt.selectionModel().currentIndex()
        model = tt.model()

        if not model.insertRow(index.row()+1, index.parent()):
            return

    def trackDelete(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())
        rowsranges = utils.re_rangebyone(sorted(rows), count=True)

        # delete tracks from bottom to keep the right indices
        for s, e in reversed(rowsranges):
            tt.model().removeRows(s,e)

        self.statusUpdate()

    def trackReset(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().trackReset(row)
        self.statusUpdate()

    def trackSanitizeArtistName(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().sanitizeArtistName(row)

    def trackSearchToArtistName(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().searchToArtistName(row)
        self.statusUpdate()

    def trackArtistNameToSearch(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().artistNameToSearch(row)
        self.statusUpdate()

    def trackArtistToSearch(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().artistToSearch(row)
        self.statusUpdate()

    def trackNameToSearch(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().nameToSearch(row)
        self.statusUpdate()

    def trackNameCutToSearch(self):
        tt = self.tableimport
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt.model().nameCutToSearch(row)
        self.statusUpdate()


    def trackSanitizeTrackNo(self):
        tt = self.tableimport
        tt.model().sanitizeTrackNo()
        self.tableimport.resizeColumnsToContents()

    def modelfeedback(self, ss):
        if ss == "updatestatus":
            self.statusUpdate()

    def statusUpdate(self):
        """ enable/disable ok btn, show some information on the status line """
        total, new, selected, left, warnnum, warngroup = self.importdata.getStatus()
        warn = ""
        if warnnum:
            warn = "!!NUMBERS!!"
        if warngroup:
            warn += "!!GROUP!!"
        if left:
            warn += "!!LEFT!!"
        if warn:
            warn = "          " + warn
        self.statuslbl.setText("T{} / N{} / S{} / L{}{}".format(total, new, selected, left, warn))
        self.ignorewarningscb.setVisible(warnnum or warngroup)
        enable = (left == 0) and (self.ignorewarningscb.isChecked() or not warn)
        self.okbtn.setEnabled(enable)

    def statusSetIgnoreWarnings(self, checked):
        self.statusUpdate()

    def statusSetFavGroup(self, checked):
        self.importdata.setFav(self.favcb.isChecked())


class ImportModel(QtCore.QAbstractTableModel):
    # a feedback signal for the window - if new filter rules means that inputs should change
    # this feedback will be used to notify the mainwindow
    feedback = QtCore.pyqtSignal(str)#, str)

    def __init__(self, importdata, parent=None):
        super().__init__(parent)
        self.importdata = importdata

    def headerData(self, section, orientation=QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self.importdata.header(section)
        else:
            return section

    def columnCount(self, parent=None):
        return self.importdata.headerCount()

    def rowCount(self, parent=None):
        return self.importdata.rowCount()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return self.importdata.data(index.row(), index.column(), (role == QtCore.Qt.EditRole))
        elif role == QtCore.Qt.ToolTipRole:
            return self.importdata.tip(index.row(), index.column())
        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if self.importdata.editable(index.column()):
            return super().flags(index) | QtCore.Qt.ItemIsEditable
        else:
            return super().flags(index)

    def getSelection(self, selected):
        rows = []
        def processIndex(idx):
            if idx != None and idx.isValid() and not idx.row() in rows:
                rows.append(idx.row())
        if selected == None or len(selected) == 0:
            return rows
        for idx in selected:
            processIndex(idx)
        return sorted(rows)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            morechanged, ok = self.importdata.setdata(index.row(), index.column(), value)
            if not ok: return False
            self.dataChanged.emit(index, index)
            if morechanged != None and len(morechanged) > 0:
                for col in morechanged:
                    idx = self.createIndex(index.row(), col , object=0)
                    self.dataChanged.emit(index, index)
            self.feedback.emit("updatestatus")
            return True
        return False

    def insertRows(self, position, rows, index=None):
        if index == None:
            index = QtCore.QModelIndex()

        self.beginInsertRows(QtCore.QModelIndex(), position, position+rows-1)
        self.importdata.insertrows(position, rows)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, index=None):
        '''
        '''
        if index == None:
            index = QtCore.QModelIndex()
        self.beginRemoveRows(QtCore.QModelIndex(), position, position+rows-1)
        self.importdata.removerows(position, rows)
        self.endRemoveRows()
        self.feedback.emit("updatestatus")
        return True

    def trackReset(self, row):
        self.importdata.reset(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def sanitizeArtistName(self, row):
        self.importdata.sanitizeArtistName(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def searchToArtistName(self, row):
        self.importdata.searchToArtistName(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def artistNameToSearch(self, row):
        self.importdata.artistNameToSearch(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def artistToSearch(self, row):
        self.importdata.artistToSearch(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def nameToSearch(self, row):
        self.importdata.nameToSearch(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def nameCutToSearch(self, row):
        self.importdata.nameCutToSearch(row)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def sanitizeTrackNo(self):
        self.importdata.sanitizeTrackNo()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.importdata.rowCount(), self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def rating(self, row, rr):
        self.importdata.rating(row, rr)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def toggleNewFlag(self, row, value=None):
        self.importdata.toggleNewFlag(row, value)
        self.dataChanged.emit(self.createIndex(row, 0), self.createIndex(row, self.importdata.headerCount()-1))
        self.feedback.emit("updatestatus")

    def isStar(self, index):
        return self.importdata.isStar(index.column())

    def isCheck(self, index):
        return self.importdata.isCheck(index.column())
