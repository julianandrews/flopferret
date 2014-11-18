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

"""A class to store a weighted range of hands"""

import eval7
import eval7.range_string

class HandRange(dict):

    def __init__(self, range_str=None):
        super(HandRange, self).__init__(self)
        self.set_zeros()
        if not range_str is None:
            self._from_str(range_str)

    def _from_str(self, range_str):
        hand_str_list = eval7.range_string.string_to_hands(range_str)
        for hand in self:
            self[hand] = 0.0
        for hand, weight in hand_str_list:
            self[hand] += weight
        self.normalize()

    def set_zeros(self):
        d = eval7.Deck()
        for i in range(51):
            for j in range(i+1, 52):
                key = (d[j], d[i])
                self[key] = 0.0

    def set_uniform(self):
        N = 1.0/1326
        for hand in self:
            self[hand] = N

    def normalize(self):
        """Normalize the hand range and return the original total."""
        total = sum(self.values())
        if not total == 0.0:
            N = 1.0/total
            for hand, weight in self.iteritems():
                self[hand] = weight*N
        return total

    def exclude_cards(self, cards):
        for hand in self:
            for card in cards:
                if card in hand:
                    self[hand] = 0.0
        return self.normalize()

    def filter(self, func):
        for hand, weight in self.iteritems():
            if not weight == 0.0:
                if not func(hand):
                    self[hand] = 0.0
        return self.normalize()

    def filtered(self, func):
        new = HandRange()
        new.update(self)
        new.filter(func)
        return new

