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

from PySide2 import QtGui, QtWidgets


class PercentDisplayWidget(QtWidgets.QWidget):
    """A simple percentage display widget with a bar and numerical label.

    usage: wid = PercentDisplayWidget()
           wid.setValue(0.8)
    """

    def __init__(self, value=0.0, max_bar_width=250.0, color='#000000'):
        super(PercentDisplayWidget, self).__init__()
        self.value = value
        self.max_bar_width = max_bar_width
        self.color = color
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(11, 0, 11, 0)
        self.spacer = QtWidgets.QSpacerItem(0, 0)
        self.label = QtWidgets.QLabel()
        layout.addSpacerItem(self.spacer)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedWidth(80 + self.max_bar_width)
        self.setValue(self.value)

    def setValue(self, value):
        """Set the value to display (0 <= value <= 1)."""
        if value < 0 or value > 1:
            raise ValueError('Only values between 0 and 1 are supported')
        self.value = value
        self.label.setText("{:.2f}%".format(self.value*100))
        self.repaint()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        box_height = self.size().height()
        bar_width = self.max_bar_width*self.value
        self.spacer.changeSize(bar_width, 0)
        color = QtGui.QColor(self.color)
        qp.setPen(QtGui.QPen(color))
        qp.setBrush(QtGui.QBrush(color))
        qp.drawRect(0, int(round(box_height/4.0)), bar_width,
                    int(round(box_height/2.0)))
