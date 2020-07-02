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


import eval7


class HandRange(dict):
    """A class to store a weighted range of hands. Each hand is a pair
    of cards with the higher card (by deck order) first."""
    def __init__(self, range_string=None):
        super(HandRange, self).__init__(self)
        self._set_zeros()
        if range_string is not None:
            self._from_str(range_string)

    def _from_str(self, range_string):
        # Load range from range-string.
        hand_str_list = eval7.rangestring.string_to_hands(range_string)
        for hand, weight in hand_str_list:
            self[hand] += weight
        self.normalize()

    def _set_zeros(self):
        # Initialize range with zeros.
        deck = eval7.Deck()
        for i, card in enumerate(deck[:-1]):
            for other_card in deck[i+1:]:
                self[(other_card, card)] = 0.0  # Higher card must be first!

    def normalize(self):
        """Normalize the hand range. Return the original total."""
        total = sum(self.values())
        if not total == 0.0:
            N = 1.0/total
            for hand, weight in self.items():
                self[hand] = weight*N
        return total

    def exclude_cards(self, cards):
        """Remove `cards` from range and renormalize."""
        for hand in self:
            for card in cards:
                if card in hand:
                    self[hand] = 0.0
        return self.normalize()
