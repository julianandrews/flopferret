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

from . import hand_range

hand_types = [
    "High Card",
    "Pair",
    "Two Pair",
    "Trips",
    "Straight",
    "Flush",
    "Full House",
    "Quads",
    "Straight Flush"
]
draw_types = ["Flush Draw", "OESD", "Gutshot"]
pair_types = ["Over Pair", "Top Pair", "Second Pair", "Low Pair", "Board Pair"]


class BoardTexture(dict):
    def __init__(self):
        for key in hand_types + draw_types + pair_types:
            self[key] = 0.0

    def calculate(self, hand_range_string, board_card_strings):
        """Calculate the probabilities of each hand type."""
        for key in hand_types + draw_types + pair_types:
            self[key] = 0.0
        board = list(map(eval7.Card, board_card_strings))
        hr = hand_range.HandRange(hand_range_string)
        hr.exclude_cards(board)
        if len(board) < 3:
            raise ValueError("Not enough cards in board!")
        for hand, prob in hr.items():
            if not prob == 0.0:
                cards = board + list(hand)
                result = eval7.evaluate(cards)
                hand_type = eval7.handtype(result)
                self[hand_type] += prob
                if len(cards) < 7 and hand_types.index(hand_type) < 5:
                    # No flush or better, so there may be draws.
                    if self.check_flush_draw(cards):
                        self["Flush Draw"] += prob
                    if hand_type != 'Straight':
                        straight_draw_type = self.check_straight_draw(cards)
                        if straight_draw_type is not None:
                            self[straight_draw_type] += prob
                if hand_type == "Pair":
                    # Break down pairs by type.
                    self[self.pair_type(hand, board)] += prob

    @staticmethod
    def check_flush_draw(cards):
        """Determine if `cards` contain a flush draw."""
        suit_counts = [0, 0, 0, 0]
        for card in cards:
            suit_counts[card.suit] += 1
        return max(suit_counts) == 4

    @staticmethod
    def check_straight_draw(cards):
        """Determine if `cards` contain an OESD or Gutshot."""
        bits = 0
        # Build a bitmask for the card ranks.
        for card in cards:
            bits |= 2 << card.rank
            if card.rank == 12:
                bits |= 1  # Bottom bit represents the low ace.

        # Look for '11110' or '1011101' (Open Ended Straight Draw)
        for i in range(9):
            s = bits >> i
            if s & 31 == 30 or s & 127 == 93:
                return 'OESD'

        # Look for Gutshot bit patterns
        for i in range(10):
            if (bits >> i) & 31 in (30, 29, 27, 23, 15):
                return 'Gutshot'
        return None

    @staticmethod
    def pair_type(hand, board):
        """Determine the kind of pair, assuming one pair hand."""
        rank_counts = [0]*13
        board_ranks = sorted(c.rank for c in board)
        hand_ranks = [c.rank for c in hand]
        for r in board_ranks + hand_ranks:
            rank_counts[r] += 1
        pair_rank = rank_counts.index(2)
        if pair_rank not in hand_ranks:
            return "Board Pair"
        elif pair_rank > board_ranks[-1]:
            return "Over Pair"
        elif pair_rank == board_ranks[-1]:
            return "Top Pair"
        elif pair_rank >= board_ranks[-2]:
            return "Second Pair"
        else:
            return "Low Pair"
