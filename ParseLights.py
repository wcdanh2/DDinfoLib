#! /usr/bin/python3

import xml.etree.ElementTree as ET
import json
from collections import OrderedDict
import os

import DD_utils


#COM string table:
#str_wave_transition_d_torch_tooltip_title  Splendorous
#colours/base.colours.darkest


light_files = ['dlc/735730_color_of_madness/scripts/raid_settings.json']

#the raid_settings file is 'special' Instead of 'id' it uses 'key'
#there may be other caveats TBD
def loadRaid_Settings(file_list, key):
    Infos = {}
    for path in file_list:
        libpath = os.path.join(DD_utils.DDpath, path)
        #if the path doesn't exist fail loud so nothing is missed.
        if os.path.exists(libpath):
            with open(libpath, 'r') as fp:
                tempInfo = json.load(fp)
            for entry in tempInfo[key]:
                #if 'quirks' key doesnt exist fail loud, it is important to know that nothing is missed.
                Infos[entry['key']] = entry
        else:
            print("Could not find {}".format(libpath))
            exit(1)
    return Infos


def parse_lights():
    misc_strings = DD_utils.misc_strings
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    light_dict = {}

    light_dict['miasma']      = {'id':'wave_farm',
                                 'name':DD_utils.remove_tags(misc_strings['str_wave_farm_torch_tooltip_title']).replace("[","").replace("]",""),
                                 'color':'default'}
    light_dict['gleaming']    = {'id':'wave_transition_a',
                                 'name':DD_utils.remove_tags(misc_strings['str_wave_transition_a_torch_tooltip_title']).replace("[","").replace("]",""),
                                 'color':'Red'}
    light_dict['blazing']     = {'id':'wave_transition_b',
                                 'name':DD_utils.remove_tags(misc_strings['str_wave_transition_b_torch_tooltip_title']).replace("[","").replace("]",""),
                                 'color': 'Blue'}
    light_dict['haunting']    = {'id':'wave_transition_c',
                                 'name':DD_utils.remove_tags(misc_strings['str_wave_transition_c_torch_tooltip_title']).replace("[","").replace("]",""),
                                 'color': 'Green'}
    light_dict['splendorous'] = {'id':'wave_transition_d',
                                 'name':DD_utils.remove_tags(misc_strings['str_wave_transition_d_torch_tooltip_title']).replace("[","").replace("]",""),
                                 'color':'Yellow'}

    #load all of the info files
    lightInfos = loadRaid_Settings(light_files, 'torch_settings_data_table')
    #load all of the buff files
    buffInfos = DD_utils.getBuffInfos()

    for light_id in light_dict:
        light_out = light_dict[light_id]
        heroBuffs = []
        monsterBuffs = []
        for buff in lightInfos[light_out['id']]['data']['hero_buff_list']:
            heroBuffs.append(DD_utils.getStringFromBuff(buffInfos[buff]))
        for buff in lightInfos[light_out['id']]['data']['monster_buff_list']:
            monsterBuffs.append(DD_utils.getStringFromBuff(buffInfos[buff]))
        light_out['heroBuffs'] = heroBuffs
        light_out['monsterBuffs'] = monsterBuffs

    #blazing's buffs contain a duplicate in the game's json, remove it
    light_dict['blazing']['heroBuffs'].pop(1)

    with open(DD_utils.out_dir+'lights.json', 'w') as fp:
        json.dump(light_dict, fp, indent=4, separators=DD_utils.separators, sort_keys=False)

#main
def main():
    parse_lights()

if __name__ == "__main__":
    main()



