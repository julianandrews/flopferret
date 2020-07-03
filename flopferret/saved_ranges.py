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

"""Simple interface to FlopFerret config file"""

import json
import os
import sys

if sys.platform.startswith('linux'):
    import xdg.BaseDirectory
    data_dir = xdg.BaseDirectory.xdg_data_home
elif sys.platform == 'win32':
    data_dir = os.getenv('APPDATA')

config_dir = os.path.join(data_dir, "flopferret")
config_filename = os.path.join(config_dir, "hand_ranges.json")


def load():
    """Load data from FlopFerret config file."""
    try:
        with open(config_filename, 'r') as f:
            data = json.load(f)
        return data
    except IOError:
        return {}


def dump(data):
    """Dump data to FlopFerret config file."""
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open(config_filename, "w+") as f:
        json.dump(data, f)
