import os.path
import math

from PyQt4 import QtCore
from PyQt4 import QtGui

from ui.mainWindowUI import Ui_MainWindow
from ui.groupsmodel import GroupsModel
from ui.tracksmodel import TracksModel
from ui.tracksdelegate import TracksDelegate
from ui.importWindow import ImportWindow
import ui.regaudio_rc

from model import model, grouptrack, group
from model.importdata import ImportData
from model.config import CFG, CFGLOC
from var import utils

WARNMSG="""The config file "{0}" didn't exist, so a default one has been created.

This also means that the default location for the database has been chosen - "{1}".
To change it, edit the configuration file and restart this application.
"""""

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.filterhistory = []
        self.lastdirectory = None # last used directory in file dialogs
        self.nowfiltering = False # whether the filter is currently processing or no
        self.nowgroupfiltering = False # whether the group filter is -||-
        #self.found = -1 # total in the selected group / all tracks
        #self.new = -1 # total new in the *shown* tracks
        #self.total = -1
        self.prevgroup = None

        # icons
        icn = QtGui.QIcon(":/regaudio.icon.48.png")
        icn.addFile(":/regaudio.icon.32.png")
        icn.addFile(":/regaudio.icon.24.png")
        icn.addFile(":/regaudio.icon.16.png")
        self.setWindowIcon(icn)

        # show a warning in case of no configuration
        self.showDBWarning()

        # setup status
        self.statusline = QtGui.QLabel()
        self.statusBar().addWidget(self.statusline)

        # models
        self.datamdl = model.Model()
        self.stats = self.datamdl.stats # share statistics
        self.tracks = TracksModel(self.datamdl.getTracks())
        self.groups = GroupsModel(self.datamdl.getGroups())

        #connect feedback first
        self.tracks.feedback.connect(self.modelfeedback)
        self.groups.feedback.connect(self.modelfeedback)

        # set table
        self.trackstable.setModel(self.tracks)
        self.trackstable.setItemDelegate(TracksDelegate(self.tracks))
        self.trackstable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.trackstable.customContextMenuRequested.connect(self.tracksContextMenu)
        self.trackstable.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.SelectedClicked |
            QtGui.QAbstractItemView.EditKeyPressed )
        self.trackstable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        # set groups
        self.filtergroups = QtGui.QSortFilterProxyModel(self)
        self.filtergroups.setSourceModel(self.groups)
        self.filtergroups.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.groupbox.setModel(self.filtergroups)
        self.groupbox.currentIndexChanged.connect(self.groupSet)
        self.groupallbtn.clicked.connect(self.actionGroupAllTracks.activate)
        self.groupfavouritebtn.clicked.connect(self.actionGroupFavourite.activate)
        self.groupnewbtn.setMenu(self.menuGroupNewImport)
        self.groupnewbtn.clicked.connect(self.groupnewbtn.showMenu)
        self.groupdeletebtn.clicked.connect(self.actionGroupDelete.activate)
        self.grouprenamebtn.clicked.connect(self.actionGroupRename.activate)
        self.groupfilterbtn.toggled.connect(self.groupFilterBool)
        self.groupfilterline.editingFinished.connect(self.groupFilter)
        self.groupfilterline.setEnabled(False)
        self.groupfilterline.setVisible(False)

        # set paging
        self.pagemaxtracksline.setText("100")
        self.pagepageline.setText("1")
        self.pagemaxtracksline.setValidator(QtGui.QIntValidator())
        self.pagepageline.setValidator(QtGui.QIntValidator())
        self.pagemaxtracksline.editingFinished.connect(self.filterSet)
        self.pagepageline.editingFinished.connect(self.filterSet)
        self.pagenextbtn.clicked.connect(self.pagenext)
        self.pageprevbtn.clicked.connect(self.pageprev)

        #connect filter
        self.filterline.editingFinished.connect(self.filterSet)
        self.actionFilterReset.triggered.connect(self.filterSetTo)
        self.menuFilterHistory.aboutToShow.connect(self.filterHistoryUpdateMenu)
        self.filterreset.clicked.connect(self.actionFilterReset.activate)
        self.filterrecall.setMenu(self.menuFilterHistory)        
        self.filterrecall.clicked.connect(self.filterrecall.showMenu)                

        #connect actions
        self.actionTrackDelete.triggered.connect(self.trackDelete)
        self.actionTrackNew.triggered.connect(self.trackNew)
        self.actionTrackToggleNew.triggered.connect(self.trackToggleNew)
        self.actionTrackDetachedCopy.triggered.connect(self.trackDetachedCopy)
        receivermm = lambda : self.groupimport(what="mm")
        self.actionImport.triggered.connect(receivermm)
        self.actionQuit.triggered.connect(self.quit)

        self.actionGroupAllTracks.triggered.connect(self.groupAllTracks)
        self.actionGroupFavourite.triggered.connect(self.groupFavorite)
        self.actionGroupNew.triggered.connect(self.groupNew)

        receivercue = lambda : self.groupimport(what="cue")
        self.actionGroupImportCue.triggered.connect(receivercue)#self.groupImportCue)
        receiverdir = lambda : self.groupimport(what="dir")
        self.actionGroupImportDirectory.triggered.connect(receiverdir)#self.groupImportDir)
        self.actionGroupDelete.triggered.connect(self.groupDelete)
        self.actionGroupRename.triggered.connect(self.groupRename)

        self.menuTrack.aboutToShow.connect(self.updateMenuTrack)
        self.menuTrackMerge.aboutToShow.connect(self.updateMenuTrackMerge)
        self.menuTrackInGroups.aboutToShow.connect(self.updateMenuTrackInGroups)
        self.menuTrackAddToGroup.aboutToShow.connect(self.updateMenuTrackAddToGroup)
        self.menuTrackRelink.aboutToShow.connect(self.updateMenuTrackRelink)

        for act in [["0", lambda : self.trackRating(0), "`"],
                   ["1", lambda : self.trackRating(1), "1"],
                   ["2", lambda : self.trackRating(2), "2"],
                   ["3", lambda : self.trackRating(3), "3"],
                   ["4", lambda : self.trackRating(4), "4"],
                   ["5", lambda : self.trackRating(5), "5"],
                   ["6", lambda : self.trackRating(6), "6"],
                   ["7", lambda : self.trackRating(7), "7"],
                   ["8", lambda : self.trackRating(8), "8"],
                   ["9", lambda : self.trackRating(9), "9"],
                   ["10", lambda : self.trackRating(10), "0"]]:
                action = QtGui.QAction(self)
                action.setText(act[0])
                action.triggered.connect(act[1])
                if len(act) == 3:
                    action.setShortcut(QtGui.QKeySequence.fromString(act[2]))
                self.menuRating.addAction(action)
                self.trackstable.addAction(action)

        # this feeds all the default settings to the model and read the data from db
        self.filterSet()
        # FIXME the following causes that the model is refreshed three times

        self.tracks.sortingreallyenabled = False
        self.trackstable.sortByColumn(0,QtCore.Qt.AscendingOrder)
        self.trackstable.setSortingEnabled(True)
        self.tracks.sortingreallyenabled = True

        self.statusupdate()

    def showDBWarning(self):
        if CFG["regaudio"]["default"] == "True":
            QtGui.QMessageBox.warning(self, "Default database",
                    WARNMSG.format(CFGLOC, CFG["regaudio"]["db"])
                    , buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)

    def statusupdate(self):
        self.statusline.setText(self.stats.status())
        #sline = ""
        #if self.found >= 0:
        #    sline += "{} tracks found".format(self.found)
        #if self.new > 0 and self.new != self.found:
        #    if sline:
        #        sline += " "
        #    sline += "{} new".format(self.new)
        #if self.total > 0 and self.total != self.found:
        #    sline += " ({} total tracks)".format(self.total)
        #if sline != "":
        #    self.statusline.setText(sline)

    def pagesset(self):
        val = self.pagepageline.validator() # int validator
        val.setBottom(1)
        maxtr = int(self.pagemaxtracksline.text())
        if maxtr == 0:
            pages = 1
        elif self.stats.fltr == 0:
            pages = 1
        else:
            pages = int(self.stats.fltr / maxtr)
            if self.stats.fltr % maxtr:
                pages += 1
        self.pagemaxpagelbl.setText("/ {}".format(pages))
        val.setTop(pages)

        self.pagebuttons()
        self.statusupdate()

    def pagenext(self):
        page = int(self.pagepageline.text())
        self.pagepageline.setText(str(page+1))
        self.filterSet()
        self.pagebuttons()

    def pageprev(self):
        page = int(self.pagepageline.text())
        if page == 0:
            return
        self.pagepageline.setText(str(page-1))
        self.filterSet()
        self.pagebuttons()

    def pagebuttons(self):
        page = int(self.pagepageline.text())
        pagemin = self.pagepageline.validator().bottom()
        pagemax = self.pagepageline.validator().top()
        self.pagenextbtn.setEnabled(page != pagemax)
        self.pageprevbtn.setEnabled(page != pagemin)

    def updateMenuTrack(self):
        tt = self.trackstable
        rows = tt.model().getSelection(tt.selectedIndexes())
        gtmode = tt.model().dbmodel.gtmode
        # new track is always enabled
        # delete should be enabled only if there are tracks selected
        self.actionTrackDelete.setEnabled(len(rows) > 0)
        # merge should be enabled only if there is more than one track selected
        #self.menuTrackMerge.setEnabled(not gtmode and (len(rows) > 1))
        self.menuTrackMerge.setEnabled(len(rows) > 1)
        # add to group and groups list should be enabled if some tracks are selected
        self.menuTrackAddToGroup.setEnabled(len(rows) > 0)
        self.menuTrackInGroups.setEnabled(len(rows) > 0)
        self.menuTrackRelink.clear()
        self.menuTrackRelink.setEnabled(len(rows) == 1 and gtmode)
        self.actionTrackDetachedCopy.setEnabled(gtmode)

    def updateMenuTrackMerge(self):
        self.menuTrackMerge.clear()

        tt = self.trackstable
        dbmodel = tt.model().dbmodel
        rows = tt.model().getSelection(tt.selectedIndexes())

        for row in rows:
            tt = dbmodel.lst[row]
            if dbmodel.gtmode:
                tt = tt.track
            receiver = lambda row=row: self.trackMerge(rows, row)
            self.menuTrackMerge.addAction(tt.menucaption(), receiver)

    def updateMenuTrackInGroups(self):
        self.menuTrackInGroups.clear()

        tt = self.trackstable
        dbmodel = tt.model().dbmodel
        rows = tt.model().getSelection(tt.selectedIndexes())

        # first - make a dict of all the K: group id, V: number of tracks that share the same group
        gid_trscaps = {}
        for row in rows:
            tt = dbmodel.lst[row]
            if type(tt) == grouptrack.GroupTrack:
                tt = tt.track
            for gt in tt.grouptracks:
                gid = gt.group.idno # group id
                trs = gid_trscaps.setdefault(gid, [0,gt.group.name])[0] + 1 # tracks in that group
                gid_trscaps[gid][0] = trs

        # if no groups were found make only an informative menu entry
        if len(gid_trscaps) == 0:
            self.menuTrackInGroups.addAction("No group found")
            return

        for gid,cntcap in sorted(gid_trscaps.items(), key=lambda x:x[1][1]):
            receiver = lambda gid=gid: self.groupFocusGid(gid, True)
            #caption = gid_caps[gid]
            caption = cntcap[1]
            count = cntcap[0]
            if count > 1:
                caption = "({} tracks)  {}".format(count, caption)
            self.menuTrackInGroups.addAction(caption, receiver)

    def updateMenuTrackAddToGroup(self):
        # show maximum MAXGROUPS, show favorites and regular groups if there is at most MAXFAV_RATIO * MAXGROUPS favorites
        MAXGROUPS = 10
        MAXFAV_RATIO = 0.5

        self.menuTrackAddToGroup.clear()

        mg = self.groups
        mt = self.trackstable.model()

        gdb = self.groups.dbmodel
        tdb = self.trackstable.model().dbmodel

        #if mt.dbmodel.gtmode:
        #    self.menuTrackAddToGroup.addAction("Not available for group tracks")
        #    return

        tt = self.trackstable
        rows = tt.model().getSelection(tt.selectedIndexes())

        # each of the tracks can be in multiple groups
        gid_cnt = {}
        for row in rows:
            tt = tdb.lst[row]
            if mt.dbmodel.gtmode:
                tt = tt.track
            for gt in tt.grouptracks:
                gid = gt.group.idno # group id
                gid_cnt[gid] = gid_cnt.get(gid, 0) + 1 # tracks in that group

        nogrps = MAXGROUPS
        if gdb.favs >= MAXGROUPS * MAXFAV_RATIO and gdb.favs < MAXGROUPS:
            nogrps = MAXGROUPS

        showpicker = (nogrps < len(gdb.lst))

        for gg in gdb.lst:
            if gg is None:
                continue
            nogrps -= 1
            receiver = lambda gid=gg.idno: self.trackAddToGroup(rows, gid)
            caption = gg.menucaption()
            if gg.idno in gid_cnt:
                caption = "({}) ".format(gid_cnt[gg.idno]) + caption
            self.menuTrackAddToGroup.addAction(caption, receiver)
            if nogrps == 0:
                break
        if showpicker:
            receiver = lambda gid=gg.idno: self.trackAddToGroup(rows, None)
            self.menuTrackAddToGroup.addAction("Pick from all ...", receiver)

    def updateMenuTrackRelink(self):
        rows = self.tracks.getSelection(self.trackstable.selectedIndexes())

        assert(len(rows) == 1)

        self.menuTrackRelink.clear()

        for tid,cap in self.tracks.dbmodel.similar(rows[0]):
            receiver = lambda tid=tid:self.trackRelink(tid)
            self.menuTrackRelink.addAction(cap, receiver)
        
    def updateMenuGroup(self):
        pass

    def getlastdirectory(self):
        """return last visited directory for file dialogs"""
        ll = self.lastdirectory
        if not ll:
            return os.path.expanduser("~")
        while not os.path.exists(ll) and ll:
            ll = os.path.dirname(ll)
        if not ll:
            return os.path.expanduser("~")
        return ll

    def groupimport(self, what):
        import os.path

        if what == "mm":
            source = QtGui.QFileDialog.getOpenFileName(self,
                    caption='Select a MM file', directory=self.getlastdirectory(),
                    filter='Freemind files (*.mm);;All files (*.*)')
        elif what == "cue":
            source = QtGui.QFileDialog.getOpenFileNames(self,
                    caption='Select a Cue file', directory=self.getlastdirectory(),
                    filter='Cue files (*.cue);;All files (*.*)')
        elif what == "dir":
            source = QtGui.QFileDialog.getExistingDirectory(self,
                    caption='Select a directory to import', directory=self.getlastdirectory(),
                    options=QtGui.QFileDialog.ShowDirsOnly)

        if source is None or len(source) == 0:
            return

        if type(source) is str:
            self.lastdirectory = source
        else:
            self.lastdirectory = source[0]

        imp = ImportData(self.datamdl, source)
        what2, msg = imp.readdatapre(what, source)
        if what2:
            result = QtGui.QMessageBox.question(self, "Importing data", msg
                                                   , buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                                                   , defaultButton=QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                what = what2

        imp.readdata(what, source)

        iw = ImportWindow(imp, parent=self)
        if not iw.exec_():
            return

        self.groups.beginResetModel()
        gid = imp.store(self.datamdl.getTracks().stats)
        self.groups.dbmodel.loadgroups()
        self.groups.endResetModel()
        self.groupFocusGid(gid)
        #self.groupbox.model().layoutChanged.emit()
        #self.trackstable.model().layoutChanged.emit()

    def groupFilterBool(self, ignored):
        self.groupFilter(focusfilter=True)

    def groupFilter(self, forcefilter=None, focusfilter=False):
        if self.nowgroupfiltering:
            return

        self.nowgroupfiltering = True
        try:
            if forcefilter != None:
                self.groupfilterline.setText(forcefilter)
                self.groupfilterbtn.setChecked(forcefilter != "")
            dofilter = self.groupfilterbtn.isChecked()
            self.groupfilterline.setVisible(dofilter)
            self.groupfilterline.setEnabled(dofilter)
            if not dofilter:
                self.groupfilterline.setText("")
            elif focusfilter:
                self.groupfilterline.setFocus(QtCore.Qt.OtherFocusReason)
            txt = self.groupfilterline.text()
            self.filtergroups.setFilterWildcard(txt)
        finally:
            self.nowgroupfiltering = False

    def groupSet(self):
        self.prevgroup = None
        self.filterSet()

    def groupNew(self):
        groupname, ok = QtGui.QInputDialog.getText(self, "New group", "New group name:")
        if not ok:
            return
        #newidx = self.groupbox.model().newGroup(groupname)
        newidx = self.groups.newGroup(groupname)
        if newidx == -1:
            QtGui.QMessageBox.warning(self, "New group",
                    "Couldn't create the group! Such group already exists!")
            return

        self.groupFocus(newidx, refresh=True)

    def groupDelete(self):
        #idx = self.groupbox.currentIndex()
        fidx = self.filtergroups.index(self.groupbox.currentIndex(), 0)
        idx = self.filtergroups.mapToSource(fidx).row()
        if idx == 0:
            QtGui.QMessageBox.warning(self, "A warning", "All Tracks is not a group", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return

        #mm = self.groupbox.model()
        name = self.groups.getGroup(idx).name

        result = QtGui.QMessageBox.question(self, "Delete?", "Delete the group '" + name + "' ?"
                                                   , buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
                                                   , defaultButton=QtGui.QMessageBox.No)
        if result != QtGui.QMessageBox.Yes:
            return

        self.groups.removeRows(idx, 1)
        #self.groupFocus(0, refresh=True)

    def groupRename(self):
        #idx = self.groupbox.currentIndex()
        fidx = self.filtergroups.index(self.groupbox.currentIndex(), 0)
        idx = self.filtergroups.mapToSource(fidx)
        idx = idx.row()
        if idx == 0:
            QtGui.QMessageBox.warning(self, "A warning",
                    "All Tracks is not a group!",
                    buttons=QtGui.QMessageBox.Ok,
                    defaultButton=QtGui.QMessageBox.NoButton)
            return

        #mm = self.groupbox.model()
        #name = mm.getGroup(self.groupbox.currentIndex()).name
        name = self.groups.getGroup(idx).name

        groupname, ok = QtGui.QInputDialog.getText(self, "Rename group",
                "Change group name:" + " "*30, text=name)
        if not ok:
            return False

        if groupname == name:
            return

        # this will in turn change the index too (handled by feedback)
        #self.groups.setData(self.groups.index(idx, 0, QtCore.QModelIndex()), groupname, QtCore.Qt.EditRole)
        newidx = self.groups.renameGroup(idx, groupname)
        if newidx == None:
            QtGui.QMessageBox.warning(self, "Rename group",
                    "Couldn't rename the group! Such group already exists!")
            return
        self.groupFocus(newidx)

    def groupFavorite(self):
        #newidx = self.groupbox.model().favorite(self.groupbox.currentIndex())
        fidx = self.filtergroups.index(self.groupbox.currentIndex(), 0)
        idx = self.filtergroups.mapToSource(fidx).row()
        if idx == 0:
            QtGui.QMessageBox.warning(self, "A warning",
                    "All Tracks is not a group!",
                    buttons=QtGui.QMessageBox.Ok,
                    defaultButton=QtGui.QMessageBox.NoButton)
            return

        newidx = self.groups.favorite(idx)

        if newidx == -1:
            return
        self.groupFocus(newidx)

    def groupAllTracks(self):
        if self.prevgroup:
            self.groupFocus(self.prevgroup, refresh=True)
            self.prevgroup = None
        else:
            fidx = self.filtergroups.index(self.groupbox.currentIndex(), 0)
            idx = self.filtergroups.mapToSource(fidx).row()
            self.prevgroup = idx
            if self.prevgroup == 0:
                self.prevgroup = None

            self.groupFilter("")
            self.groupbox.blockSignals(True)
            self.groupbox.setCurrentIndex(0)
            self.groupbox.blockSignals(False)
            self.filterSet()

    def groupFocusGid(self, gid, refresh=False):
        self.groupFocus(self.groups.dbmodel.gidToIdx(gid), refresh)

    def groupFocus(self, idx, refresh=False):
        # this functions is called whener groups have changed, lets invalidate the model
        #self.filtergroups.invalidate()
        # the idx is points to the original model, its integer
        # if the idx cannot be remapped to the new reset the filter and try to focus it again
        idx = self.groups.index(idx, 0)
        idxmap = self.filtergroups.mapFromSource(idx)
        if not idxmap.isValid():
            self.groupFilter("") # reset the filter
            idxmap = self.filtergroups.mapFromSource(idx)
            if not idxmap.isValid():
                raise ValueError("groupFocus: invalid group row index {}".format(idx.row()))

        self.prevgroup = None
        self.groupbox.setCurrentIndex(idxmap.row())
        if refresh:
            self.filterSet()

    def trackAddToGroup(self, rows, gid):
        if gid == None:
            # show picker of all the groups
            db = self.groups.dbmodel
            lst = db.getcaptions()
            name, ok = QtGui.QInputDialog.getItem(self, "Pick a group",
                    "Pick the group to add the tracks into",
                    lst, current=0, editable=False)
            # the captions don't include the All tracks group so ..
            if not ok:
                return
            idx = lst.index(name) # slooow
            idx += 1
            gid = db.lst[idx].idno

        d, dc = self.trackstable.model().dbmodel.addtogroup(rows, gid)
        if not d:
            return

        result = QtGui.QMessageBox.question(self, "Add tracks to group", \
                "The tracks\n\t{}\nare already in that group?\n\nDo you wish to add them anyway?".format(dc), \
                buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                defaultButton=QtGui.QMessageBox.No)
        if result != QtGui.QMessageBox.Yes:
            return
        self.trackstable.model().dbmodel.addtogroup(d, gid, force=True)
        self.filterSet()

    def trackDelete(self):
        tt = self.trackstable
        dbmodel = tt.model().dbmodel
        rows = tt.model().getSelection(tt.selectedIndexes())
        rowsranges = utils.re_rangebyone(sorted(rows), count=True)

        if tt.model().dbmodel.gtmode:
            result = QtGui.QMessageBox.question(self, "Delete grouptracks", \
                    "Delete just the selected group tracks (yes) or also the tracks (all)?", \
                    buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.YesAll , \
                    defaultButton=QtGui.QMessageBox.No)
        else:
            result = QtGui.QMessageBox.question(self, "Delete tracks", \
                    "PERMAMENTLY delete the selected tracks?", \
                    buttons=QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, \
                    defaultButton=QtGui.QMessageBox.No)
        if result != QtGui.QMessageBox.Yes and result != QtGui.QMessageBox.YesAll:
            return

        # delete tracks from bottom to keep the right indices
        for s, e in reversed(rowsranges):
            tt.model().removeRows(s,e, trackstoo=(result == QtGui.QMessageBox.YesAll))

    def trackNew(self):
        index = self.trackstable.selectionModel().currentIndex()
        model = self.trackstable.model()

        if not model.insertRow(index.row()+1, index.parent()):
            return

        #self.updateActions()

        #for column in range(model.columnCount(index.parent())):
        #    child = model.index(index.row()+1, column, index.parent())
        #    model.setData(child, "[No lst]", QtCore.Qt.EditRole)

    def trackRating(self, rr):
        tt = self.trackstable
        dbmodel = tt.model().dbmodel
        rows = tt.model().getSelection(tt.selectedIndexes())
        tt.model().rating(rows, rr)

    def trackToggleNew(self):
        tt = self.trackstable
        dbmodel = tt.model().dbmodel
        rows = tt.model().getSelection(tt.selectedIndexes())
        tt.model().toggleNew(rows)

    def trackMerge(self, rows, torow):
        index = self.trackstable.selectionModel().currentIndex()
        model = self.trackstable.model()

        model.mergetracks(rows, torow)

    def trackDetachedCopy(self):
        rows = self.tracks.getSelection(self.trackstable.selectedIndexes())
        assert(len(rows) == 1)
        self.tracks.detachedcopy(rows[0])

    def trackRelink(self, tid):
        """link selected grouptrack to the track given by the id"""
        rows = self.tracks.getSelection(self.trackstable.selectedIndexes())
        assert(len(rows) == 1)
        self.tracks.relink(rows[0], tid)

    def tracksContextMenu(self, point):
        point.setX(point.x() + self.trackstable.verticalHeader().width())
        point.setY(point.y() + self.trackstable.horizontalHeader().height())
        self.menuTrack.exec_(self.trackstable.mapToGlobal(point))

    def filterSetTo(self, rule=""):
        # work around action triggred
        if not type(rule) is str:
            rule = ""
        self.filterline.setText(rule)
        self.filterSet()

    def filterHistoryUpdateMenu(self):
        self.menuFilterHistory.clear()
        for rule in reversed(self.filterhistory):
            receiver = lambda rule=rule: self.filterSetTo(rule)
            self.menuFilterHistory.addAction(rule, receiver)

    def filterSet(self):#, *args, **kvargs):
        if self.nowfiltering:
            return

        # get values from controls
        try:
            self.nowfiltering = True
            rule = self.filterline.text().strip().lower()
            if rule and (not self.filterhistory or self.filterhistory[-1] != rule):
                if rule in self.filterhistory:
                    self.filterhistory.remove(rule)
                # limit the size of the history to 20 entries
                if len(self.filterhistory) >= 19:
                    self.filterhistory = self.filterhistory[-19:]
                self.filterhistory.append(rule)
                if not self.filterrecall.isEnabled():
                    self.filterrecall.setEnabled(True)
           
            grp = group.Group.namefromcaption(self.groupbox.currentText())
            maxrows = int(self.pagemaxtracksline.text())
            page = int(self.pagepageline.text())

            self.tracks.setfilter(rule=rule, group=grp, maxrows=maxrows, page=page)
            
            if self.tracks.rowCount():
                pass # TODO maybe remember the rule if the search yielded any results
        finally:
            self.pagebuttons()
            self.nowfiltering = False

    def modelfeedback(self, name, value):
        '''
        process feedback from the underlying model(s)

        see also Feedback class

        messages are passed in the form of the name and value
        the name is the common name of the control or command
        the value is the value to be set

        the feedback should not cause any updates so the nowfiltering is set to true
        (nowfiltering causes that filterSet doesn't work)
        '''
        setlock = False
        try:
            if not self.nowfiltering:
                self.nowfiltering = True
                setlock = True
            if name == "group": # by m/gm/setData
                self.groupFocus(int(value))
            elif name == "statusupdate":
                self.statusupdate()
            elif name == "pagesset":
                self.pagesset()
            #elif name == "total":
            #    self.total = int(value)
            #    self.statusupdate()
            elif name == "page": # by m/m/setfilter
                self.pagepageline.setText(value)
            #elif name == "rule":
            #    self.filterline.setText(value)
            #elif name == "found":
            #    self.found = int(value)
            #    self.pagesset()
            #elif name == "new":
            #    self.new = (int(value))
            #    self.statusupdate()
            elif name == "max": # by m/m/setfilter
                self.pagemaxtracksline.setText(value)
            elif name == "resize": # by u/tm/sort and setfilter
                self.trackstable.resizeColumnsToContents()
                self.trackstable.resizeRowsToContents()
            elif name == "sortbycol": # by m/m/setfilter
                cc = (int(value))
                sign = cc > 0
                cc = cc - 1 if sign else - 1 - cc
                try:
                    self.trackstable.horizontalHeader().blockSignals(True)
                    #self.trackstable.blockSignals(True)
                    self.trackstable.horizontalHeader().setSortIndicator(cc,
                            QtCore.Qt.AscendingOrder if sign else QtCore.Qt.DescendingOrder)
                finally:
                    #self.trackstable.blockSignals(False)
                    self.trackstable.horizontalHeader().blockSignals(False)
            else:
                print("Unknown feedback received", name, value)
        finally:
            if setlock:
                self.nowfiltering = False

    def quit(self):
        self.close()

