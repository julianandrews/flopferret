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

"""Main Board Texture Analyzer Gui"""

from PySide import QtCore, QtGui

import board_texture
import percent_display
import range_selector
import range_string
import saved_ranges

class MainWindow(QtGui.QWidget):
    """The Main Window of the Application."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.board_texture = board_texture.BoardTexture()

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Flop Ferret")
        
        main_layout = QtGui.QVBoxLayout(self)
        input_layout = self.make_input_layout()
        output_layout = self.make_output_layout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)
        self.setLayout(main_layout)

        self.show()

    def make_input_layout(self):
        self.range_input = QtGui.QLineEdit()
        self.range_validator = RangeValidator()
        self.range_validator.saved_ranges = saved_ranges.load()
        self.range_input.setValidator(self.range_validator)
        self.board_input = QtGui.QLineEdit()
        self.board_input.setValidator(BoardValidator())
        self.board_input.setMaximumWidth(100)
        set_range_button = QtGui.QPushButton("Set Range")
        set_range_button.clicked.connect(self.set_range)
        board_label = QtGui.QLabel("Board")

        layout = QtGui.QGridLayout()
        layout.addWidget(set_range_button, 0, 0)
        layout.addWidget(self.range_input, 0, 1)
        layout.addWidget(board_label, 1, 0)
        layout.addWidget(self.board_input, 1, 1)
        self.range_input.textChanged.connect(self.check_input_state)
        self.range_input.textChanged.emit("")
        self.board_input.textChanged.connect(self.check_input_state)
        self.board_input.textChanged.emit("")
        return layout

    def make_output_layout(self):
        self.outputs = {}
        for key, value in self.board_texture.iteritems():
            output = percent_display.PercentDisplayWidget(value, 
                    max_bar_width=100, color="#00BED4")
            self.outputs[key] = output
        
        layout = QtGui.QGridLayout()
        hand_type_label = QtGui.QLabel("<b>Hand Type Breakdown</b>")
        pair_label = QtGui.QLabel("<b>Pair Breakdown</b>")
        draw_label = QtGui.QLabel("<b>Draw Breakdown</b>")
        layout.addWidget(hand_type_label, 0, 0, 1, 2)
        
        def add_output(key, row, column, name=None):
            name = name or key
            label = QtGui.QLabel(name)
            label.setContentsMargins(30, 0, 0, 0)
            layout.addWidget(label, row, column)
            layout.addWidget(self.outputs[key], row, column+1)

        for i, (key, name) in enumerate(zip(board_texture.hand_types, 
                board_texture.readable_hand_types)):
            add_output(key, i+1, 0, name)
        layout.addWidget(pair_label, 0, 2, 1, 2)
        for i, key in enumerate(board_texture.pair_types):
            add_output(key, i+1, 2)
        layout.addWidget(draw_label, i+2, 2, 1, 2)
        for j, key in enumerate(board_texture.draw_types):
            add_output(key, i+j+3, 2)
        return layout

    def check_input_state(self, *args, **kwargs):
        """Check if a QLineEdit has a valid input, and set the color
        appropriately. Used by the range and board inputs."""
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)
        if state[0] == QtGui.QValidator.Acceptable:
            color = '#b2ebf2' # light blue
        elif state[0] == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.calculate()

    def set_range(self):
        """Open a RangeSelector dialog to set range_input"""
        selector = range_selector.RangeSelector(self)
        text = self.range_input.text()
        validator = self.range_input.validator()
        if validator.validate(text, 0)[0] == QtGui.QValidator.Acceptable:
            selector.set_from_range_string(text)
        if selector.exec_():
            text = selector.range_string()
            self.range_input.setText(text)
        self.range_validator.saved_ranges = saved_ranges.load()

    def calculate(self):
        """Calculate the board texture and display the results."""
        if not self.range_input.hasAcceptableInput() or \
                not self.board_input.hasAcceptableInput():
            return
        hr_string = self.range_input.text()
        board_string = self.board_input.text().replace(" ", "")
        board = [board_string[i:i+2] for i in 
                range(0, len(board_string)-1, 2)]
        self.board_texture.calculate(hr_string, board)
        for key, output in self.outputs.iteritems():
            output.setValue(self.board_texture[key])

class RangeValidator(QtGui.QValidator):
    """Validator for range input."""

    def validate(self, s, pos):
        if range_string.validate_string(s):
            # replace tags with saved ranges
            tags = s.split('#')[1::2] 
            for tag in tags:
                matches = [x for x in self.saved_ranges if x[0] == tag]
                if not len(matches) == 0:
                    new_str = matches[0][1]
                    s = s.replace("#{}#".format(tag), new_str)
                    pos = len(s)
            # fix case of tokens
            in_tag = False
            new_s = ""
            for c in s:
                if c == '#':
                    # a parseable string always has properly completed tags
                    in_tag = not in_tag
                if not in_tag and c in ''.join(range_string.ranks).lower():
                    c = c.upper()
                new_s += c
            return [QtGui.QValidator.Acceptable, new_s, pos]
        else:
            # accept any input as intermediate 
            return [QtGui.QValidator.Intermediate, s, pos]

class BoardValidator(QtGui.QRegExpValidator):
    """Validator for board input."""

    _rank_str = ''.join(range_string.ranks)+''.join(range_string.ranks).lower()
    _suit_str = ''.join(range_string.suits)
    _card_str = "[{}][{}]".format(_rank_str, _suit_str)
    _board_str = "({}( *)?){{3,5}}".format(_card_str)
    _re = QtCore.QRegExp(_board_str)
    _partial_card = "(({})|[{}]|[{}])".format(_card_str, _rank_str, _suit_str)
    _int_re = QtCore.QRegExp("({}( *)?){{0,5}}".format(_partial_card))

    def __init__(self):
        super(BoardValidator, self).__init__(self._re)

    def validate(self, s, pos):
        result, s, new_pos = super(BoardValidator, self).validate(s, pos)
        if result == QtGui.QValidator.Acceptable:
            # prevent duplicate cards and fix spaces
            strip_pos = len(s[:new_pos].replace(" ", ""))
            s = s.replace(" ", "")
            card_strs = [s[i:i+2] for i in range(0, len(s)-1, 2)]
            if any(card_strs.count(x) > 1 for x in card_strs):
                result = QtGui.QValidator.Invalid
            s = " ".join(card_strs)
            new_pos = strip_pos + (strip_pos)/2-1
            # make ranks upper case
            for r in range_string.ranks:
                s = s.replace(r.lower(), r)
        elif result == QtGui.QValidator.Invalid:
            # loosen standard for intermediate matches
            if self._int_re.exactMatch(s):
                result = QtGui.QValidator.Intermediate
                new_pos = pos
        return [result, s, new_pos]

