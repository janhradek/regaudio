#!/usr/bin/env python

# this is an extended example of QStyledItemDelegate use
# based on stardelegate.py from PyQt demos

# These are only needed for Python v2 but are harmless for Python v3.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import math

from PyQt4 import QtCore, QtGui


class StarPainter(object):
    # enum EditMode
    Editable, ReadOnly = range(2)

    PaintingScaleFactor = 20

    def __init__(self, starCount=1, maxStarCount=5):
        self._starCount = starCount
        self._maxStarCount = maxStarCount

        # STANDING STAR - looks ugly
        #self.starPolygon = QtGui.QPolygonF([QtCore.QPointF(0.5, 0.0)])
        #for i in range(6):
        #    self.starPolygon << QtCore.QPointF(0.5 + 0.5 * math.cos(1.5*math.pi + (0.8 * i * math.pi)),
        #                                       0.5 + 0.5 * math.sin(1.5*math.pi + (0.8 * i * math.pi)))

        self.starPolygon = QtGui.QPolygonF()
        for i in range(11):
            mul = 0.5 if not i % 2 else 0.2
            self.starPolygon << QtCore.QPointF(0.5 + mul * math.cos(0.2 * i * math.pi),
                                               0.5 + mul * math.sin(0.2 * i * math.pi))

        self.halfStarPolygon = QtGui.QPolygonF()
        for i in range(3,9):
            mul = 0.5 if not i % 2 else 0.2
            self.halfStarPolygon << QtCore.QPointF(0.5 + mul * math.cos(0.2 * i * math.pi),
                                               0.5 + mul * math.sin(0.2 * i * math.pi))

    def starCount(self):
        return self._starCount

    def maxStarCount(self):
        return self._maxStarCount

    def setStarCount(self, starCount):
        self._starCount = starCount

    def setMaxStarCount(self, maxStarCount):
        self._maxStarCount = maxStarCount

    def sizeHint(self):
        return self.PaintingScaleFactor * QtCore.QSize(self._maxStarCount, 1)

    def paint(self, painter, rect, palette, selected, editMode):
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        #painter.setPen(QtCore.Qt.NoPen)

        pen = QtGui.QPen()
        if editMode == StarPainter.Editable:
            painter.setBrush(palette.highlight())
            pen.setBrush(palette.highlight())
        elif selected:
            painter.setBrush(palette.highlightedText())
            pen.setBrush(palette.highlightedText())
        else:
            painter.setBrush(palette.foreground())
            pen.setBrush(palette.foreground())
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(0.07) # TODO could be a setting?

        painter.setPen(pen)

        yOffset = (rect.height() - self.PaintingScaleFactor) / 2
        painter.translate(rect.x(), rect.y() + yOffset)
        painter.scale(self.PaintingScaleFactor, self.PaintingScaleFactor)

        for i in range(0, 2*self._maxStarCount, 2):
            if i + 1 == self._starCount:
                painter.setPen(QtCore.Qt.NoPen)
                painter.drawPolygon(self.halfStarPolygon, QtCore.Qt.WindingFill)
                painter.setPen(pen)
                painter.drawPolyline(self.starPolygon)
            elif i < self._starCount:
                painter.drawPolygon(self.starPolygon, QtCore.Qt.WindingFill)
            else: #elif editMode == StarPainter.Editable: 
                painter.drawPolyline(self.starPolygon)

            painter.translate(1.0, 0.0)

        painter.restore()

class CheckPainter(object):
    PaintingScaleFactor = 20

    def __init__(self, state=True):
        self.state = state
        self.circlerect = QtCore.QRectF(0.0,0.0,1.0,1.0)
        self.starlines = []
        for i in range(5):
            ang = (0.4 * i + 1.5) * math.pi
            self.starlines.append(QtCore.QLineF(0.5 + 0.2 * math.cos(ang), 0.5 + 0.2 * math.sin(ang),
                0.5 + 0.3 * math.cos(ang), 0.5 + 0.3 * math.sin(ang))) 

    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state

    def sizeHint(self):
        return self.PaintingScaleFactor * QtCore.QSize(1, 1)

    def paint(self, painter, rect, palette, selected):
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        #painter.setPen(QtCore.Qt.NoPen)

        pen = QtGui.QPen()
        if selected:
            #painter.setBrush(palette.highlightedText())
            pen.setBrush(palette.highlightedText())
        else:
            #painter.setBrush(palette.foreground())
            pen.setBrush(palette.foreground())
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        pen.setWidthF(0.15)
        painter.setPen(pen)

        yOffset = (rect.height() - self.PaintingScaleFactor) / 2
        xOffset = (rect.width() - self.PaintingScaleFactor) / 2
        painter.translate(rect.x() + xOffset, rect.y() + yOffset)
        painter.scale(self.PaintingScaleFactor, self.PaintingScaleFactor)

        painter.drawEllipse(self.circlerect)
        
        if self.state:
            pen.setWidthF(0.2)
            painter.setPen(pen)
            painter.drawLines(self.starlines)

        painter.restore()

class StarEditor(QtGui.QWidget):

    editingFinished = QtCore.pyqtSignal()

    def __init__(self, starPainter, parent = None):
        super().__init__(parent)

        self._starPainter = starPainter #StarPainter()

        self.setMouseTracking(True)
        self.setAutoFillBackground(True)

    def setStarRating(self, value):
        self._starPainter.setStarCount(value)

    def starRating(self):
        return self._starPainter.starCount()

    def sizeHint(self):
        return self._starPainter.sizeHint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self._starPainter.paint(painter, self.rect(), self.palette(), False,
                StarPainter.Editable)

    def mouseMoveEvent(self, event):
        star = self.starAtPosition(event.x())

        if star != self._starPainter.starCount() and star != -1:
            self._starPainter.setStarCount(star)
            self.update()

    def mouseReleaseEvent(self, event):
        self.editingFinished.emit()

    def starAtPosition(self, x):
        # Enable a halfstar, if pointer crosses the center horizontally.
        halfstarwidth = self._starPainter.sizeHint().width() // (2*self._starPainter.maxStarCount())
        halfstar = int(x + halfstarwidth / 2) // halfstarwidth
        if 0 <= halfstar <= 2*self._starPainter.maxStarCount():
            return halfstar 

        return -1


class TracksDelegate(QtGui.QStyledItemDelegate):
    """
    allows to paint stars instead of rating (0-10) and a nice graphic instead of True/False

    constructor requires an object that implements isStar(index) 
    and isCheck(index) methods to distinguish when to paint those

    """
    def __init__(self, paintSelector, parent=None):
        super().__init__(parent)
        self.ps = paintSelector # must implement isStar(index) and isCheck(index)
        self.sp = StarPainter()
        self.cp = CheckPainter()

    def paint(self, painter, option, index):
        dd = index.data()
        selected = False
        if self.ps.isStar(index) and dd != None:
            self.sp.setStarCount(dd)
            if option.state & QtGui.QStyle.State_Selected:
                selected = True
                painter.fillRect(option.rect, option.palette.highlight())
            self.sp.paint(painter, option.rect, option.palette, selected, StarPainter.ReadOnly)
        elif self.ps.isCheck(index) and dd != None:
            self.cp.setState(dd)
            if option.state & QtGui.QStyle.State_Selected:
                selected = True
                painter.fillRect(option.rect, option.palette.highlight())
            self.cp.paint(painter, option.rect, option.palette, selected)
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        dd = index.data()
        if self.ps.isStar(index) and dd != None:
            return self.sp.sizeHint()
        elif self.ps.isCheck(index) and dd != None:
            return self.cp.sizeHint()
        else:
            return super().sizeHint(option, index)

    def createEditor(self, parent, option, index):
        dd = index.data()
        if self.ps.isStar(index) and dd != None:
            editor = StarEditor(StarPainter(), parent)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        elif self.ps.isCheck(index) and dd != None:
            return None
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        dd = index.data()
        if self.ps.isStar(index) and dd != None:
            editor.setStarRating(dd)
        elif self.ps.isCheck(index) and dd != None:
            pass
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        dd = index.data()
        if self.ps.isStar(index) and dd != None:
            model.setData(index, editor.starRating(), QtCore.Qt.EditRole)
        elif self.ps.isCheck(index) and dd != None:
            newValue = not bool(index.model().data(index, QtCore.Qt.DisplayRole))
            model.setData(index, newValue, QtCore.Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        if self.ps.isCheck(index):
            if not index.flags() & QtCore.Qt.ItemIsEditable:
                return False
    
            # Do not change the checkbox-state
            if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
                if event.button() != QtCore.Qt.LeftButton:# or not self.getCheckBoxRect(option).contains(event.pos()):
                    return False
                if event.type() == QtCore.QEvent.MouseButtonDblClick:
                    return True
            elif event.type() == QtCore.QEvent.KeyPress:
                if event.key() != QtCore.Qt.Key_Space and event.key() != QtCore.Qt.Key_Select:
                    return False
            else:
                return False
    
            # Change the checkbox-state
            self.setModelData(None, model, index)
            return True
        else:
            return super().editorEvent(event, model, option, index)
    
    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        #self.closeEditor.emit(editor)
        self.closeEditor.emit(editor, QtGui.QStyledItemDelegate.NoHint)


def populateTableWidget(tableWidget):
    staticData = (
        ("Mass in B-Minor", "Baroque", "J.S. Bach", False, 5),
        ("Three More Foxes", "Jazz", "Maynard Ferguson", False, 4),
        ("Sex Bomb", "Pop", "Tom Jones", True,  3),
        ("Barbie Girl", "Pop", "Aqua", True, 5),
    )

    for row, (title, genre, artist, new, rating) in enumerate(staticData):
        item0 = QtGui.QTableWidgetItem(title)
        item1 = QtGui.QTableWidgetItem(genre)
        item2 = QtGui.QTableWidgetItem(artist)
        item3 = QtGui.QTableWidgetItem(new)
        #item3.setData(0, StarPainter(rating))
        item3.setData(0, new)
        item4 = QtGui.QTableWidgetItem(rating)
        #item3.setData(0, StarPainter(rating))
        item4.setData(0, rating)
        tableWidget.setItem(row, 0, item0)
        tableWidget.setItem(row, 1, item1)
        tableWidget.setItem(row, 2, item2)
        tableWidget.setItem(row, 3, item3)
        tableWidget.setItem(row, 4, item4)

class PaintSelector(object):
    def isStar(self, index):
        if index.column() == 4:
            return True
        return False

    def isCheck(self, index):
        if index.column() == 3:
            return True
        return False

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    tableWidget = QtGui.QTableWidget(4, 5)
    tableWidget.setItemDelegate(TracksDelegate(PaintSelector()))
    tableWidget.setEditTriggers(
            QtGui.QAbstractItemView.DoubleClicked |
            QtGui.QAbstractItemView.SelectedClicked)
    tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    headerLabels = ("Title", "Genre", "Artist", "New", "Rating")
    tableWidget.setHorizontalHeaderLabels(headerLabels)

    populateTableWidget(tableWidget)

    tableWidget.resizeColumnsToContents()
    tableWidget.resize(500, 300)
    tableWidget.show()

    sys.exit(app.exec_())
