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

"""A Range selector widget for Hold'em hand ranges."""

from PySide2 import QtGui, QtCore, QtWidgets

import eval7

from . import saved_ranges


class RangeSelector(QtWidgets.QDialog):

    def __init__(self, parent):
        super(RangeSelector, self).__init__(parent)
        self.single_hands = [[], [], [], []]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Range Selector")
        self.setModal(True)

        main_layout = QtWidgets.QVBoxLayout()
        grid = self.layout_button_grid()
        weight_selector = self.layout_weight_selector()
        h_box = QtWidgets.QHBoxLayout()
        h_box.addLayout(grid)
        v_box = QtWidgets.QVBoxLayout()
        v_box.addLayout(weight_selector)
        self.saved_ranges = QtWidgets.QComboBox()
        self.saved_ranges.setEditable(True)
        re = QtCore.QRegExp("^\w{1,12}$")
        self.saved_ranges.setValidator(QtGui.QRegExpValidator(re))
        self.load_data()
        self.saved_ranges.currentIndexChanged.connect(self.load_range)
        save_button = QtWidgets.QPushButton("Save")
        save_button.clicked.connect(self.save_range)
        delete_button = QtWidgets.QPushButton("Delete")
        delete_button.clicked.connect(self.delete_range)
        v_box.addWidget(self.saved_ranges)
        v_box.addWidget(save_button)
        v_box.addWidget(delete_button)
        h_box.addLayout(v_box)
        main_layout.addLayout(h_box)
        self.percent_label = QtWidgets.QLabel()
        main_layout.addWidget(self.percent_label)
        single_hand_layout = self.layout_single_hand_input()
        main_layout.addLayout(single_hand_layout)
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            parent=self,
        )
        main_layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.setLayout(main_layout)

        self.setFixedSize(self.sizeHint())
        self.set_percent_label()
        self.show()

    def layout_button_grid(self):
        grid = QtWidgets.QGridLayout()
        self.grid_buttons = {}
        grid.setSpacing(0)
        for x in range(13):
            for y in range(13):
                if x < y:
                    suitedness = 's'
                elif x > y:
                    suitedness = 'o'
                else:
                    suitedness = ''
                label = eval7.rangestring.ranks[12-min(x, y)] + \
                    eval7.rangestring.ranks[12-max(x, y)] + suitedness
                button = RangeSelectorButton(label, suitedness)
                button.clicked.connect(
                    # lambda token=label: self.handle_click(token)
                    (lambda token: (lambda: self.handle_click(token)))(label)
                )
                self.grid_buttons[label] = button
                grid.addWidget(button, x, y)
        return grid

    def layout_weight_selector(self):
        layout = QtWidgets.QFormLayout()
        labels = ["Weight {}".format(i) for i in range(1, 5)]
        self.weight_selector = QtWidgets.QComboBox()
        self.weight_selector.addItems(labels)
        self.weight_spinners = []
        self.weight_selector.currentIndexChanged.connect(self.update_display)
        layout.addRow("Weight", self.weight_selector)
        for label in labels:
            spin_box = QtWidgets.QSpinBox()
            spin_box.setMinimum(0)
            spin_box.setMaximum(10000)
            spin_box.setSuffix("%")
            layout.addRow(label, spin_box)
            self.weight_spinners.append(spin_box)
        return layout

    def layout_single_hand_input(self):
        single_hand_layout = QtWidgets.QFormLayout()
        self.single_hand_input = QtWidgets.QLineEdit()
        self.single_hand_input.setValidator(SingleHandListValidator())
        self.single_hand_input.textChanged.connect(self.check_input_state)
        single_hand_layout.addRow("Individual Hands:", self.single_hand_input)
        self.single_hand_input.textChanged.emit("")
        return single_hand_layout

    def update_display(self):
        i = self.weight_selector.currentIndex()
        for token, button in self.grid_buttons.items():
            button.setChecked(button.weights[i])
        self.set_percent_label()
        self.set_single_hand_input()
        self.repaint()

    def handle_click(self, token):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        i = self.weight_selector.currentIndex()
        tokens = [t for (t, w) in eval7.rangestring.string_to_tokens(token + '+')]
        if modifiers == QtCore.Qt.ShiftModifier:
            state = True
        elif modifiers == QtCore.Qt.ControlModifier:
            state = False
        else:
            state = not self.grid_buttons[token].weights[i]
            tokens = [token]
        for t in tokens:
            button = self.grid_buttons[t]
            button.weights[i] = state
        self.purge_duplicate_singles()
        self.set_percent_label()
        self.update_display()

    def clear(self):
        for button in self.grid_buttons.values():
            button.weights = [False, False, False, False]
        self.single_hands = [[], [], [], []]
        for spinner in self.weight_spinners:
            spinner.setValue(100)

    def load_data(self):
        data = saved_ranges.load()
        for (name, range_str) in data.items():
            self.saved_ranges.addItem(name, userData=range_str)
        if len(data) == 0:
            self.saved_ranges.addItem("", userData="")

    def save_range(self):
        name = self.saved_ranges.currentText()
        if name == "":
            # some sort of feedback maybe?
            return
        range_str = self.range_string()
        i = self.saved_ranges.findText(name)
        if i > 0:
            self.saved_ranges.setItemData(i, range_str)
        else:
            self.saved_ranges.addItem(name, userData=range_str)
        self.write_ranges()

    def load_range(self):
        i = self.saved_ranges.currentIndex()
        data = self.saved_ranges.itemData(i)
        self.set_from_range_string(data)

    def write_ranges(self):
        data = {self.saved_ranges.itemText(i): self.saved_ranges.itemData(i)
                for i in range(self.saved_ranges.count())}
        return saved_ranges.dump(data)

    def delete_range(self):
        i = self.saved_ranges.currentIndex()
        if not i == 0:
            self.saved_ranges.removeItem(i)
            self.write_ranges()

    def check_input_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)
        if state[0] == QtGui.QValidator.Acceptable:
            color = '#b2ebf2'  # light blue
            i = self.weight_selector.currentIndex()
            tokens = eval7.rangestring.string_to_tokens(state[1])
            self.single_hands[i] = [t for (t, w) in tokens]
            self.purge_duplicate_singles()
            self.set_percent_label()
        elif state[0] == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def purge_duplicate_singles(self):
        for i in range(len(self.single_hands)):
            for token, button in self.grid_buttons.items():
                if button.weights[i]:
                    hands = [''.join(x)
                             for x in eval7.rangestring.token_to_hands(token)]
                    self.single_hands[i] = [
                        h for h in self.single_hands[i] if h not in hands
                    ]
            self.single_hands[i] = list(set(self.single_hands[i]))
        self.set_single_hand_input()

    def set_percent_label(self):
        combos = self.combos()
        prob = combos/13.26
        plural_string = '' if combos == 1 else 's'
        s = "<b>{} combo{}, {:.2f}%</b>.".format(combos, plural_string, prob)
        self.percent_label.setText(s)

    def set_single_hand_input(self):
        i = self.weight_selector.currentIndex()
        token_list = [(t, 1.0) for t in self.single_hands[i]]
        s = eval7.rangestring.tokens_to_string(token_list)
        self.single_hand_input.setText(s)

    def set_from_range_string(self, s):
        tokens = eval7.rangestring.string_to_tokens(s)
        self.clear()
        weights = sorted(set(w for (t, w) in tokens), reverse=True)
        if 1.0 in weights:
            weights.remove(1.0)
            weights = [1.0] + weights
        elif len(weights) == 0:
            weights = [1.0]
        weights = weights[:4] + (4-len(weights))*[1.0]
        for i, w in enumerate(weights):
            self.weight_spinners[i].setValue(int(round(100*w)))
        for t, w in tokens:
            if t[0] == '#':
                continue
            i = weights.index(w)
            if len(t) == 4:
                self.single_hands[i].append(t)
            else:
                self.grid_buttons[t].weights[i] = True
        self.update_display()

    def combos(self, i=None):
        combo_counts = {"": 6, "s": 4, "o": 12}
        i = i or self.weight_selector.currentIndex()
        combos = 0
        for button in self.grid_buttons.values():
            if button.weights[i]:
                combos += combo_counts[button.suitedness]
        combos += len(self.single_hands[i])
        return combos

    def range_string(self):
        token_list = []
        for token, button in self.grid_buttons.items():
            for i, b in enumerate(button.weights):
                if b:
                    weight = self.weight_spinners[i].value()/100.0
                    token_list.append((token, weight))
        for i, tokens in enumerate(self.single_hands):
            weight = self.weight_spinners[i].value()/100.0
            token_list += [(token, weight) for token in tokens]
        return eval7.rangestring.tokens_to_string(token_list)


class RangeSelectorButton(QtWidgets.QPushButton):

    _colors = {'s': "#98F098", 'o': "#FF9898", '': "#9898F0"}
    _selected_colors = {'s': "#D8FFD8", 'o': "#FFD8D8", '': "#D8D8FF"}
    _weight_colors = ["#404040", "#F06000", "#800080", "#0060D0"]
    _weight_pos = [4, 8, 25, 29]
    _style = """
    QPushButton {{
        color: black;
        font-weight: bold;
        background-color: {};
        border: 1px solid black;
    }}
    QPushButton:pressed {{
        color: blue;
        padding:0;
    }}
    QPushButton:checked {{
        background-color: {};
        font-weight: bold;
        padding: 0;
    }}"""

    def __init__(self, label, suitedness):
        super(RangeSelectorButton, self).__init__()

        self.setText(label)
        self.suitedness = suitedness
        self.weights = [False, False, False, False]
        self.initUI()

    def initUI(self):
        self.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
        self.setFixedSize(35, 35)
        self.setCheckable(True)
        ss = self._style.format(
            self._colors[self.suitedness],
            self._selected_colors[self.suitedness]
        )
        self.setStyleSheet(ss)

    def paintEvent(self, event):
        super(RangeSelectorButton, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        for (i, w) in enumerate(self.weights):
            if w:
                color = self._weight_colors[i]
                pen = QtGui.QPen(color)
                painter.setPen(pen)
                painter.setBrush(QtGui.QColor(color))
                painter.drawRoundedRect(4, self._weight_pos[i], 27, 2, 1, 1)


class SingleHandListValidator(QtGui.QRegExpValidator):

    _hand_str = "[{rank}][{suit}][{rank}][{suit}]".format(
        rank=''.join(eval7.rangestring.ranks),
        suit=''.join(eval7.rangestring.suits),
    )
    _hand_list_str = "({hand}(, ?{hand})*)?".format(hand=_hand_str)
    _re = QtCore.QRegExp(_hand_list_str)

    def __init__(self):
        super(SingleHandListValidator, self).__init__(self._re)

    def validate(self, s, pos):
        result, s, pos = super(SingleHandListValidator, self).validate(s, pos)
        if result == QtGui.QValidator.Acceptable:
            stripped = s.replace(" ", "")
            hands = stripped.split(',')
            if '' in hands:
                hands.remove('')
            try:
                for hand in hands:
                    normalized = eval7.rangestring.normalize_token(hand)
                    s = s.replace(hand, normalized)
            except eval7.rangestring.RangeStringError:
                result = QtGui.QValidator.Invalid
        return [result, s, pos]
