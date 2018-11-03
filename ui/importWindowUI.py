# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'importWindowUI.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImportWindowUI(object):
    def setupUi(self, ImportWindowUI):
        ImportWindowUI.setObjectName("ImportWindowUI")
        ImportWindowUI.resize(609, 432)
        self.verticalLayout = QtWidgets.QVBoxLayout(ImportWindowUI)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupnamelbl = QtWidgets.QLabel(ImportWindowUI)
        self.groupnamelbl.setObjectName("groupnamelbl")
        self.horizontalLayout_2.addWidget(self.groupnamelbl)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.groupnamechangebtn = QtWidgets.QPushButton(ImportWindowUI)
        self.groupnamechangebtn.setObjectName("groupnamechangebtn")
        self.horizontalLayout_2.addWidget(self.groupnamechangebtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.tableimport = QtWidgets.QTableView(ImportWindowUI)
        self.tableimport.setAlternatingRowColors(True)
        self.tableimport.setShowGrid(False)
        self.tableimport.setWordWrap(False)
        self.tableimport.setObjectName("tableimport")
        self.verticalLayout.addWidget(self.tableimport)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.statuslbl = QtWidgets.QLabel(ImportWindowUI)
        self.statuslbl.setText("")
        self.statuslbl.setObjectName("statuslbl")
        self.horizontalLayout.addWidget(self.statuslbl)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.favcb = QtWidgets.QCheckBox(ImportWindowUI)
        self.favcb.setObjectName("favcb")
        self.horizontalLayout.addWidget(self.favcb)
        self.ignorewarningscb = QtWidgets.QCheckBox(ImportWindowUI)
        self.ignorewarningscb.setObjectName("ignorewarningscb")
        self.horizontalLayout.addWidget(self.ignorewarningscb)
        self.okbtn = QtWidgets.QPushButton(ImportWindowUI)
        self.okbtn.setObjectName("okbtn")
        self.horizontalLayout.addWidget(self.okbtn)
        self.cancelbtn = QtWidgets.QPushButton(ImportWindowUI)
        self.cancelbtn.setObjectName("cancelbtn")
        self.horizontalLayout.addWidget(self.cancelbtn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ImportWindowUI)
        QtCore.QMetaObject.connectSlotsByName(ImportWindowUI)

    def retranslateUi(self, ImportWindowUI):
        _translate = QtCore.QCoreApplication.translate
        ImportWindowUI.setWindowTitle(_translate("ImportWindowUI", "Import"))
        self.groupnamelbl.setText(_translate("ImportWindowUI", "Group name"))
        self.groupnamechangebtn.setText(_translate("ImportWindowUI", "Change ..."))
        self.favcb.setText(_translate("ImportWindowUI", "Favourite"))
        self.ignorewarningscb.setText(_translate("ImportWindowUI", "Ignore warnings"))
        self.okbtn.setText(_translate("ImportWindowUI", "OK"))
        self.cancelbtn.setText(_translate("ImportWindowUI", "Cancel"))

