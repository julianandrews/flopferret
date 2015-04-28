# Copyright (C) 2014 Julian Andrews
# This file is part of Flop Ferret.
#
# Flop Ferret is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Flop Ferret is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

from PySide import QtGui, QtCore

class PercentDisplayWidget(QtGui.QWidget):
    """A simple percentage display widget with a bar and numerical label.
    
    usage: wid = PercentDisplayWidget()
           wid.setValue(0.8)
    """

    def __init__(self, value=None, max_bar_width=None, color=None):
        super(PercentDisplayWidget, self).__init__()
        self.value = value or 0.0
        self.max_bar_width = max_bar_width or 250.0
        self.color = color or "#000000"
        self.initUI()

    def initUI(self):
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(11, 0, 11, 0)
        self.spacer = QtGui.QSpacerItem(0, 0)
        self.label = QtGui.QLabel()
        layout.addSpacerItem(self.spacer)
        layout.addWidget(self.label)
        self.setValue(self.value)
        self.setLayout(layout)
        self.setFixedWidth(80 + self.max_bar_width)

    def setValue(self, value):
        self.value = value
        self.label.setText("{:.2f}%".format(self.value*100))
        self.repaint()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        height = size.height()
        width = self.max_bar_width*self.value
        self.spacer.changeSize(width, 0)
        color = QtGui.QColor(self.color)
        qp.setPen(QtGui.QPen(color))
        qp.setBrush(QtGui.QBrush(color))
        qp.drawRect(0, int(round(0.25*height)), width, int(round(0.5*height)))

