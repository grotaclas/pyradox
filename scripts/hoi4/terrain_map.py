import hoi4
import csv
import os
import re
import collections
import warnings

import pyradox


definition_csv = os.path.join(pyradox.get_game_directory('HoI4'), 'map', 'definition.csv')
terrains = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('HoI4'), 'common', 'terrain', '00_terrain.txt'), verbose=False)['categories']

color_override = {
    'desert' : (255, 63, 0), # more red to avoid confusion with plains
    }

symbol_override = {
    'desert' : '⛭',
    'hills' : '△',
    'mountain' : '▲',
    'ocean' : '~',
    'lakes' : '',
    'marsh' : '⚶',
    'forest' : '♧',
    'jungle' : '♣',
    'plains' : '',
    'urban' : '⚑',
    'unknown' : '',
    }

colormap = {}
textmap = {}

with open(definition_csv) as definition_file:
    csv_reader = csv.reader(definition_file, delimiter = ';')
    for rowcount, row in enumerate(csv_reader):
        try:
            province_id = int(row[0])
            terrain_key = row[6]
            if terrain_key in color_override:
                colormap[province_id] = color_override[terrain_key]
            else:
                colormap[province_id] = tuple(c for c in terrains[terrain_key].find_all('color'))
            textmap[province_id] = symbol_override[terrain_key]
        except (ValueError, IndexError):
            if rowcount > 0:  # skip errors in the first row, because that can be a heading line
                warnings.warn('Could not parse province definition from row #%d with contents "%s" of %s.' % (
                rowcount + 1, str(row), definition_csv))

province_map = pyradox.worldmap.ProvinceMap(game = 'HoI4')
out = province_map.generate_image(colormap, default_land_color=(255, 255, 255))
province_map.overlay_text(out, textmap, fontfile = "unifont.ttf", fontsize = 16, antialias = False, default_offset = (4, -2))
pyradox.image.save_using_palette(out, 'out/terrain_map.png')
