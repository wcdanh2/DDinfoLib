#! /usr/bin/python

import xml.etree.ElementTree as ET
import json

DDpath = 'DarkestDungeon/'
out_dir = 'DDinfoLib/'
_separators = (',', ': ')


#TODO move utility functions to utility import.
def stripName(name):
    return name.replace(" ","").replace("-","").replace("'","").lower()

#remove tags like '{colour|blight}' from the strings
def remove_tags(string):
    while string.find('{')!=-1 and string.find('}')!=-1:
        string = string.replace(string[string.find('{'):string.find('}')+1],"")
        #print string
    return string


#TODO move string_tables and getLanguageDict to utils
#load the misccellaneous strings and return it as a dict of key(id):text pairs.
string_tables = ['localization/miscellaneous.string_table.xml',
                 'localization/heroes.string_table.xml',
                 'dlc/580100_crimson_court/localization/CC.string_table.xml',
                 'dlc/702540_shieldbreaker/localization/shieldbreaker.string_table.xml',
                 'dlc/735730_color_of_madness/localization/CoM.string_table.xml']
def getLanguageDict():
    misc_strings = {}
    for path in string_tables:
        tree = ET.parse(DDpath+path)
        #gets the root of the tree. Idk some weird xml thing
        root = tree.getroot()
        #I am only interested in english, so lets simplify and get a dict with just the english info.
        english = root[0]
        for line in english:
            misc_strings[line.attrib['id']] = line.text
    return misc_strings

trinketInfoFiles = ['trinkets/base.entries.trinkets.json',
    'dlc/445700_musketeer/trinkets/musketeer.entries.trinkets.json',
    'dlc/580100_crimson_court/features/crimson_court/trinkets/crimson_court.entries.trinkets.json',
    'dlc/580100_crimson_court/features/flagellant/trinkets/flagellant.entries.trinkets.json',
    'dlc/702540_shieldbreaker/trinkets/shieldbreaker.entries.trinkets.json',
    'dlc/735730_color_of_madness/trinkets/com.entries.trinkets.json',
    'dlc/735730_color_of_madness/trinkets/special_com.entries.trinkets.json']
def getTrinketInfos():
    trinketInfos = {}
    for path in trinketInfoFiles:
        with open(DDpath+path) as fp:
            tempTrinkets = json.load(fp)
        for entry in tempTrinkets['entries']:
            trinketInfos[entry['id']] = entry
    return trinketInfos

#
buffInfo_files = ['shared/buffs/base.buffs.json',
    'dlc/580100_crimson_court/features/crimson_court/shared/buffs/crimson_court.buffs.json',
    'dlc/580100_crimson_court/features/flagellant/shared/buffs/flagellant.buffs.json',
    'dlc/702540_shieldbreaker/shared/buffs/shieldbreaker.buffs.json',
    'dlc/735730_color_of_madness/shared/buffs/com.buffs.json']
def getBuffInfos():
    #open the base game buffs file and convert from list to map
    buffInfos = {}
    for path in buffInfo_files:
        with open(DDpath+path) as fp:
            tempBuffs = json.load(fp)
        for buff in tempBuffs['buffs']:
            buffInfos[buff['id']] = buff
    return buffInfos

def parse_trinkets():

    misc_strings = getLanguageDict()
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    trinket_dict = {}
    for key in misc_strings:
        if key.startswith('str_inventory_title_trinket'):
            t_id = key.replace('str_inventory_title_trinket', "")
            t_name = misc_strings[key]
            trinket_dict[t_id] = {'name': t_name, 'id': t_id }

    #load all of the trinket info files
    trinketInfos = getTrinketInfos()
    #load all of the buff files
    buffInfos = getBuffInfos()

#trinket data: name, rarity, hero_class(if any), origin, effects[list], additional(?), limit, price
    skipped_trinkets = []
    for trinket_id in trinket_dict:
        if trinket_id in trinketInfos:
            d_trinket = trinket_dict[trinket_id]
            s_trinket = trinketInfos[trinket_id]
            #name (done above)
            #rarity
            d_trinket['rarity'] = misc_strings['trinket_rarity_'+s_trinket['rarity']]  #rarity_dict[s_trinket['rarity']]
            #hero_class
            hero = ""
            if len(s_trinket['hero_class_requirements']):
                #TODO I didn't see any trinkets that had multiple hero classes, but there might be in the future.
                hero = misc_strings['hero_class_name_'+s_trinket['hero_class_requirements'][0]]#for now just using the first hero if present
            d_trinket['hero_class'] = hero
            #origin
            origin = ""
            if len(s_trinket['origin_dungeon']):
                origin = misc_strings['dungeon_name_'+s_trinket['origin_dungeon']] #dungeon_names[s_trinket['origin_dungeon']]
            d_trinket['origin_dungeon'] = origin
            #effects
            #create a list of effects as strings.
            if len(s_trinket['buffs']):
                d_trinket['buffs'] = []
                #print s_trinket['id']
                for buff_id in s_trinket['buffs']:
                    buff_info = buffInfos[buff_id]
                    rule_id = 'buff_rule_tooltip_' + buff_info['rule_type']
                    stat_str_id = 'buff_stat_tooltip_'+ buff_info['stat_type']
                    if len(buff_info['stat_sub_type']):
                        stat_str_id += '_'+buff_info['stat_sub_type']
                    try:
                        stat_str = misc_strings[stat_str_id]
                    except:
                        stat_str_id = 'buff_stat_tooltip_'+ buff_info['stat_type']
                        stat_str = misc_strings[stat_str_id]
                    #print stat_str
                    stat_str = remove_tags(stat_str)
                    amount = float(buff_info['amount'])
                    if amount <1 and amount >-1:
                        amount = amount*100 #workaround for the %fomatter not multiplying as expected
                    try:
                        stat_str = stat_str % (amount)
                    except:
                        print "WARNING: {} may have parsed incorrectly : {}".format(s_trinket['id'], stat_str)
                    base_str = misc_strings[rule_id]
                    #print base_str
                    base_str = remove_tags(base_str)
                    #print buff_id
                    #print stat_str
                    #print base_str
                    try:
                        base_str = base_str % (stat_str,buff_info['rule_data']['float'])
                    except TypeError:
                        base_str = base_str % (stat_str)
                    d_trinket['buffs'].append(base_str)

            #trinket_dict[trinket_id] = d_trinket

        else:
            #these trinkets were in the xml, but not found in trinket info
            print trinket_id + " no match"
            skipped_trinkets.append(trinket_id)

    #remove any trinkets that had a name but no info
    for trinket_id in skipped_trinkets:
        del trinket_dict[trinket_id]

    #change key to the stripped name
    trinket_output = {}
    for key in trinket_dict:
        trinket_output[stripName(trinket_dict[key]['name'])] = trinket_dict[key]

    with open(out_dir+'trinkets.json', 'w') as fp:
        json.dump(trinket_output, fp, indent=4, separators=_separators, sort_keys=True)

#main
def main():
    parse_trinkets()

if __name__ == "__main__":
    main()




