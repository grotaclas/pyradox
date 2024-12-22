import hoi4
import re
import os
import json
import hoi4
import pyradox

date = '1936.1.1'

beta = False

if beta:
    game = 'HoI4_beta'
else:
    game = 'HoI4'

localisation_sources = ['state_names']

countries = hoi4.load.get_countries()

states = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory(game), 'history', 'states'))
state_categories = pyradox.txt.parse_merge(os.path.join(pyradox.get_game_directory(game), 'common', 'state_category'),
                                         verbose=False, merge_levels = 1)

state_categories = state_categories['state_categories']

for state in states.values():
    history = state['history'].at_time(date, merge_levels = -1)
    # if state['id'] == 50: print('state50', history)
    state['owner'] = history['owner']
    state['owner_name'] = countries[history['owner']]['name']
    state['human_name'] = pyradox.yml.get_localisation(state['name'], game = game)

    country = countries[state['owner']]

    country['states'] = (country['states'] or 0) + 1

    state_category_key = state['state_category']
    state['building_slots'] = state_categories[state_category_key]['local_building_slots'] or 0
    country['building_slots'] = (country['building_slots'] or 0) + state['building_slots']
    
    if 'resources' in state:
        for resource, quantity in state['resources'].items():
            state[resource] = quantity

    for _, victory_points in history.find_all('victory_points', tuple_length = 2):
            state['victory_point_total'] = (state['victory_point_total'] or 0) + victory_points

    if 'buildings' in history:
        for building, quantity in history['buildings'].items():
            if isinstance(building, str):
                if isinstance(quantity, pyradox.Tree) and 'level' in quantity:
                    quantity = quantity['level']
                state[building] = (state[building] or 0) + quantity
            else:
                # province buildings
                for building, quantity in quantity.items():
                    if isinstance(quantity, pyradox.Tree) and 'level' in quantity:
                        quantity = quantity['level']
                    state[building] = (state[building] or 0) + quantity

def sum_keys_function(*sum_keys):
    def result_function(k, v):
        return '%d' % sum((v[sum_key] or 0) for sum_key in sum_keys)
    return result_function

columns = (
    ('ID', '%(id)s'),
    ('Name', '%(human_name)s'),
    ('Country', '{{flag|%(owner_name)s}}'),
    ('Tag', '%(owner)s'),
    ('{{Icon|vp}}', '%(victory_point_total)d'),
    ('{{Icon|pop|(M)}}', lambda k, v: '%0.2f' % ((v['manpower'] or 0) / 1e6) ),
    ('{{Icon|infra}}', '%(infrastructure)d'),
    ('State category', '%(state_category)s'),
    ('{{Icon|Building slot}}', '%(building_slots)d'),
    ('{{Icon|MIC}}', '%(arms_factory)d'),
    ('{{Icon|NIC}}', '%(dockyard)d'),
    ('{{Icon|CIC}}', '%(industrial_complex)d'),
    # ('Total factories', sum_keys_function('arms_factory', 'dockyard', 'industrial_complex')),
    ('{{Icon|Oil}}', '%(oil)d'),
    ('{{Icon|Aluminium}}', '%(aluminium)d'),
    ('{{Icon|Rubber}}', '%(rubber)d'),
    ('{{Icon|Tungsten}}', '%(tungsten)d'),
    ('{{Icon|Steel}}', '%(steel)d'),
    ('{{Icon|Chromium}}', '%(chromium)d'),
    # ('Total resources', sum_keys_function('oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium')),
    ('{{Icon|Air base}}', '%(air_base)d'),
    ('{{Icon|Naval base}}', '%(naval_base)d'),
    )

if beta:
    out_filename = "out/states_beta.txt"
else:
    out_filename = "out/states.txt"
with open(out_filename, "w") as out:
    out.write(pyradox.table.make_table(states, 'wiki', columns, sort_function = lambda key, value: value['id']))

if beta:
    csv_filename = "out/states_beta.csv"
else:
    csv_filename = "out/states.csv"

pyradox.csv.write_tree(states, csv_filename, columns, 'excel', sort_function = lambda key, value: value['id'])

if beta:
    json_filename = "out/states_beta.json"
else:
    json_filename = "out/states.json"

with open(json_filename, 'w') as f:
    pyradox.json.dump_tree(states.replace_key_with_subkey('state', 'id'), f)
