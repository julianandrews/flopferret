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

from PySide2 import QtCore, QtGui, QtWidgets
import eval7

from . import board_texture
from . import percent_display
from . import range_selector
from . import saved_ranges


class MainWindow(QtWidgets.QWidget):
    """The Main Window of the Application."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.board_texture = board_texture.BoardTexture()

        self.initUI()

    def initUI(self):
        # Build the window UI and show it.
        self.setWindowTitle("Flop Ferret")

        main_layout = QtWidgets.QVBoxLayout(self)
        input_layout = self.make_input_layout()
        output_layout = self.make_output_layout()

        main_layout.addLayout(input_layout)
        main_layout.addLayout(output_layout)

        self.setLayout(main_layout)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q),
                        self, QtCore.SLOT("close()"))
        self.show()

    def make_input_layout(self):
        # Build the layout for the inputs.
        self.range_input = QtWidgets.QLineEdit()
        self.range_validator = RangeValidator()
        self.range_validator.saved_ranges = saved_ranges.load()
        self.range_input.setValidator(self.range_validator)
        self.board_input = QtWidgets.QLineEdit()
        self.board_input.setValidator(BoardValidator())
        self.board_input.setMaximumWidth(100)
        set_range_button = QtWidgets.QPushButton("Set Range")
        set_range_button.clicked.connect(self.set_range)
        board_label = QtWidgets.QLabel("Board")

        layout = QtWidgets.QGridLayout()
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
        # Build the layout for the outputs.
        layout = QtWidgets.QGridLayout()
        # Store a dictionary of PercentDisplay outputs for easy update.
        self.outputs = {}
        for name, probability in self.board_texture.items():
            output = percent_display.PercentDisplayWidget(
                probability, max_bar_width=100, color="#00BED4"
            )
            self.outputs[name] = output

        def add_output(name, row, column):
            label = QtWidgets.QLabel(name)
            label.setContentsMargins(30, 0, 0, 0)
            layout.addWidget(label, row, column)
            layout.addWidget(self.outputs[name], row, column+1)

        # Add base hand type outputs to layout
        hand_type_label = QtWidgets.QLabel("<b>Hand Type Breakdown</b>")
        layout.addWidget(hand_type_label, 0, 0, 1, 2)
        for i, name in enumerate(board_texture.hand_types):
            add_output(name, i+1, 0)
        # Add pair breakdown outputs
        pair_label = QtWidgets.QLabel("<b>Pair Breakdown</b>")
        layout.addWidget(pair_label, 0, 2, 1, 2)
        for i, name in enumerate(board_texture.pair_types):
            add_output(name, i+1, 2)
        # Add draw breakdown outputs
        draw_label = QtWidgets.QLabel("<b>Draw Breakdown</b>")
        layout.addWidget(draw_label, i+2, 2, 1, 2)
        for j, name in enumerate(board_texture.draw_types):
            add_output(name, i+j+3, 2)

        return layout

    def check_input_state(self, *args, **kwargs):
        # Check if a QLineEdit has a valid input, and set the color
        # appropriately. Used by the range and board inputs.
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)
        if state[0] == QtGui.QValidator.Acceptable:
            color = '#b2ebf2'  # light blue
        elif state[0] == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.calculate()

    def set_range(self):
        """Open a RangeSelector dialog to set range_input"""
        selector = range_selector.RangeSelector(self)
        range_string = self.range_input.text()
        validator = self.range_input.validator()
        if validator.validate(range_string, 0)[0] == validator.Acceptable:
            selector.set_from_range_string(range_string)
        if selector.exec_():
            # Update the range input on success
            new_range_string = selector.range_string()
            self.range_input.setText(new_range_string)
        # Reload saved_ranges in case updated by selector.
        self.range_validator.saved_ranges = saved_ranges.load()

    def calculate(self):
        """Calculate the board texture and display the results."""
        if not self.range_input.hasAcceptableInput() or \
                not self.board_input.hasAcceptableInput():
            return
        range_string = self.range_input.text()
        board_string = self.board_input.text().replace(" ", "")
        board = [board_string[i:i+2] for i in range(0, len(board_string)-1, 2)]
        self.board_texture.calculate(range_string, board)
        for key, output in self.outputs.items():
            output.setValue(self.board_texture[key])


class RangeValidator(QtGui.QValidator):
    """Validator for range input."""

    def validate(self, s, pos):
        if eval7.rangestring.validate_string(s):
            # Replace tags with saved ranges.
            tags = s.split('#')[1::2]
            for tag in tags:
                new_str = self.saved_ranges.get(tag)
                if new_str is not None:
                    s = s.replace("#{}#".format(tag), new_str)
                    pos = len(s)
            # fix case of tokens
            in_tag = False
            new_s = ""
            for c in s:
                if c == '#':
                    # A parseable string always has properly completed tags.
                    in_tag = not in_tag
                if not in_tag and c in ''.join(eval7.rangestring.ranks).lower():
                    c = c.upper()
                new_s += c
            return [QtGui.QValidator.Acceptable, new_s, pos]
        else:
            # Accept any other input as intermediate.
            return [QtGui.QValidator.Intermediate, s, pos]


class BoardValidator(QtGui.QRegExpValidator):
    """Validator for board input."""
    _rank_str = ''.join(eval7.rangestring.ranks) + \
                ''.join(eval7.rangestring.ranks).lower()
    _suit_str = ''.join(eval7.rangestring.suits)
    # A card is a rank and a suit.
    _card_re_str = "[{}][{}]".format(_rank_str, _suit_str)
    # A board is 3-5 cards, optionally with spaces between them.
    _board_re = QtCore.QRegExp("({}( *)?){{3,5}}".format(_card_re_str))
    # A partial card is a card, a rank, or a suit.
    _partial_card_re_str = "(({})|[{}]|[{}])".format(
        _card_re_str, _rank_str, _suit_str
    )
    # A sequence of partial cards is an intermediate match.
    _partial_board_re = QtCore.QRegExp("({}( *)?){{0,5}}".format(
        _partial_card_re_str))

    def __init__(self):
        super(BoardValidator, self).__init__(self._board_re)

    def _get_card_strings(self, s):
        stripped = s.replace(' ', '')
        card_strings = [stripped[i:i+2].capitalize()
                        for i in range(0, len(stripped) - 1, 2)]
        if any(card_strings.count(x) > 1 for x in card_strings):
            return None
        else:
            return card_strings

    def validate(self, s, pos):
        result, s, new_pos = super(BoardValidator, self).validate(s, pos)
        if result == QtGui.QValidator.Invalid:
            # Partial cards are intermediate.
            if self._partial_board_re.exactMatch(s):
                result = QtGui.QValidator.Intermediate
                new_pos = pos
        else:
            card_strings = self._get_card_strings(s)
            if card_strings is None:
                # Duplicate cards are invalid.
                result = QtGui.QValidator.Invalid
            elif result == QtGui.QValidator.Acceptable:
                # Reposition to account for the inserted spaces.
                stripped_pos = len(s[:new_pos].replace(' ', ''))
                new_pos = stripped_pos + (stripped_pos - 1)//2
                s = ' '.join(card_strings)
        return [result, s, new_pos]
