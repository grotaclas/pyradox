import _initpath
import os
import re
import collections
from PIL import Image

import pyradox


tree = pyradox.txt.parse_file(os.path.join(pyradox.get_game_directory('EU4'), 'map', 'terrain.txt'))

# terrain.bmp is a palette image. Convert to RGB, so that getpixel returns RGB values
terrain_bmp = Image.open(os.path.join(pyradox.get_game_directory('EU4'), 'map', 'terrain.bmp')).convert('RGB')

province_map = pyradox.worldmap.ProvinceMap('EU4')

colormap = {}

for province_id, position in province_map.positions['centroid'].items():
    colormap[province_id] = tuple(terrain_bmp.getpixel(position))

for terrain_type, terrain_data in tree['categories'].items():
    if 'color' not in terrain_data: continue
    color = tuple(terrain_data.find_all('color'))
    for province_id in terrain_data.find_all('terrain_override'):
        colormap[province_id] = color


out = province_map.generate_image(colormap)
out.save('out/terrain_map.png')
