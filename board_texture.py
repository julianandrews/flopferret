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
import hand_range

hand_types = ["High Card", "Pair", "Two Pair", "Trips", "Straight", "Flush", 
    "Full House", "Quads", "Straight Flush"] 
draw_types = ["Flush Draw", "OESD", "Gutshot"]
pair_types = ["Over Pair", "Top Pair", "Second Pair", "Low Pair", "Board Pair"]

class BoardTexture(dict):

    def __init__(self):
        for key in hand_types + draw_types + pair_types:
            self[key] = 0.0

    def calculate(self, hr_str, board_strs):
        for key in hand_types + draw_types + pair_types:
            self[key] = 0.0
        board = map(eval7.Card, board_strs)
        hr = hand_range.HandRange(hr_str)
        hr.exclude_cards(board)
        if len(board) < 3:
            raise ValueError("Not enough cards in board!")
        for hand, prob in hr.iteritems():
            if not prob == 0.0:
                cards = board + list(hand)
                result = eval7.evaluate(cards)
                hand_type_index = result >> 12
                hand_type = eval7.hand_type(result)
                self[hand_type] += prob
                if len(cards) < 7: 
                    if hand_type_index < 5 and self.check_flush_draw(cards):
                        # worse than flush
                        self["Flush Draw"] += prob
                    if hand_type_index < 4: 
                        # worse than straight
                        result = self.check_straight_draw(cards)
                        if result == 2:
                            self["OESD"] += prob
                        elif result == 1:
                            self["Gutshot"] += prob
                if hand_type == "OnePair":
                    self[self.pair_type(hand, board)] += prob
                    
    @staticmethod
    def check_flush_draw(cards):
        suit_counts = [0, 0, 0, 0]
        for c in cards:
            suit_counts[c.suit] += 1
        if max(suit_counts) == 4:    
            return True
        else:
            return False

    @staticmethod
    def check_straight_draw(cards):
        rs = set(c.rank for c in cards)
        bits = 0
        for r in rs:
            bits |= (2<<r)
            if r == 12:
                bits |= 1
        for i in range(9):
            s = bits>>i
            if s&31 == 30 or s&127 == 93: #OESD!
                return 2
        for i in range(10):
            if (bits>>i)&31 in (30, 29, 27, 23, 15): # Gutshot!
                return 1
        return 0
 
    @staticmethod
    def pair_type(hand, board):
        rank_counts = [0]*13
        board_ranks = sorted(c.rank for c in board)
        hand_ranks = [c.rank for c in hand]
        for r in board_ranks + hand_ranks:
            rank_counts[r] += 1
        pair_rank = rank_counts.index(2)
        if not pair_rank in hand_ranks:
            return "Board Pair"
        elif pair_rank > board_ranks[-1]:
            return "Over Pair"
        elif pair_rank == board_ranks[-1]:
            return "Top Pair"
        elif pair_rank >= board_ranks[-2]:
            return "Second Pair"
        else:
            return "Low Pair"

