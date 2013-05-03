# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'importWindowUI.ui'
#
# Created: Thu Dec 27 09:11:56 2012
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ImportWindowUI(object):
    def setupUi(self, ImportWindowUI):
        ImportWindowUI.setObjectName(_fromUtf8("ImportWindowUI"))
        ImportWindowUI.resize(609, 432)
        self.verticalLayout = QtGui.QVBoxLayout(ImportWindowUI)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.groupnamelbl = QtGui.QLabel(ImportWindowUI)
        self.groupnamelbl.setObjectName(_fromUtf8("groupnamelbl"))
        self.horizontalLayout_2.addWidget(self.groupnamelbl)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.groupnamechangebtn = QtGui.QPushButton(ImportWindowUI)
        self.groupnamechangebtn.setObjectName(_fromUtf8("groupnamechangebtn"))
        self.horizontalLayout_2.addWidget(self.groupnamechangebtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tableimport = QtGui.QTableView(ImportWindowUI)
        self.tableimport.setAlternatingRowColors(True)
        self.tableimport.setShowGrid(False)
        self.tableimport.setWordWrap(False)
        self.tableimport.setObjectName(_fromUtf8("tableimport"))
        self.verticalLayout.addWidget(self.tableimport)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.statuslbl = QtGui.QLabel(ImportWindowUI)
        self.statuslbl.setText(_fromUtf8(""))
        self.statuslbl.setObjectName(_fromUtf8("statuslbl"))
        self.horizontalLayout.addWidget(self.statuslbl)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.favcb = QtGui.QCheckBox(ImportWindowUI)
        self.favcb.setObjectName(_fromUtf8("favcb"))
        self.horizontalLayout.addWidget(self.favcb)
        self.ignorewarningscb = QtGui.QCheckBox(ImportWindowUI)
        self.ignorewarningscb.setObjectName(_fromUtf8("ignorewarningscb"))
        self.horizontalLayout.addWidget(self.ignorewarningscb)
        self.okbtn = QtGui.QPushButton(ImportWindowUI)
        self.okbtn.setObjectName(_fromUtf8("okbtn"))
        self.horizontalLayout.addWidget(self.okbtn)
        self.cancelbtn = QtGui.QPushButton(ImportWindowUI)
        self.cancelbtn.setObjectName(_fromUtf8("cancelbtn"))
        self.horizontalLayout.addWidget(self.cancelbtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ImportWindowUI)
        QtCore.QMetaObject.connectSlotsByName(ImportWindowUI)

    def retranslateUi(self, ImportWindowUI):
        ImportWindowUI.setWindowTitle(_translate("ImportWindowUI", "Import", None))
        self.groupnamelbl.setText(_translate("ImportWindowUI", "Group name", None))
        self.groupnamechangebtn.setText(_translate("ImportWindowUI", "Change ...", None))
        self.favcb.setText(_translate("ImportWindowUI", "Favourite", None))
        self.ignorewarningscb.setText(_translate("ImportWindowUI", "Ignore warnings", None))
        self.okbtn.setText(_translate("ImportWindowUI", "OK", None))
        self.cancelbtn.setText(_translate("ImportWindowUI", "Cancel", None))

