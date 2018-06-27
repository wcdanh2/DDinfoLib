#! /usr/bin/python

import xml.etree.ElementTree as ET
import json

DDpath = 'DarkestDungeon/'
out_dir = 'DDinfoLib/'
_separators = (',', ': ')


#TODO move utility functions to utility import.
def stripName(name):
    return name.replace(" ","").replace("-","").replace("'","").lower()

def getHeroNames():
    hero_dict = {}
    tree = ET.parse(DDpath+'localization/heroes.string_table.xml')
    root = tree.getroot()
    english = root[0]
    for line in english:
        #print line.attrib
        if line.attrib['id'].startswith('hero_class_name_'):
            h_name = line.text
            h_id = line.attrib['id'].replace('hero_class_name_', "")
            hero_dict[h_id] = h_name
    return hero_dict

def getDungeonNames(english):
    d_names = {}
    for line in english:
        if line.attrib['id'].startswith('dungeon_name_'):
            d_name = line.text
            d_id = line.attrib['id'].replace('dungeon_name_', "")
            d_names[d_id] = d_name
    return d_names
#TODO it may be better to just make a dict of id/text combo's in the english section,
#then build up to the id needed, especially for the way buffs are stored.
def getBuffTooltips(english):
    tooltips = {}
    for line in english:
        if line.attrib['id'].startswith('buff_rule_tooltip_'):
            tip = line.text
            tip_id = line.attrib['id'].replace('buff_rule_tooltip_', "")
            tooltips[tip_id] = tip
    return tooltips

#load the misccellaneous strings and return it as a dict of key(id):text pairs.
def getLanguageDict():
    tree = ET.parse(DDpath+'localization/miscellaneous.string_table.xml')
    #gets the root of the tree. Idk some weird xml thing
    root = tree.getroot()
    #I am only interested in english, so lets simplify and get a dict with just the english info.
    english = root[0]
    misc_strings = {}
    for line in english:
        misc_strings[line.attrib['id']] = line.text
    return misc_strings


def parse_trinkets():

    misc_strings = getLanguageDict()
    #prints all of the trinket names and adds them to the trinket dict
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    trinket_dict = {}
    for key in misc_strings:
        if key.startswith('str_inventory_title_trinket'):
            t_id = key.replace('str_inventory_title_trinket', "")
            t_name = misc_strings[key]
            trinket_dict[t_id] = {'name': t_name }
#        elif line.attrib['id'].startswith('trinket_rarity_'):
#            rarity_key = line.attrib['id'].replace('trinket_rarity_', "")
#            rarity_dict[rarity_key] = line.text

    hero_dict = getHeroNames()
    #making the dungeon names in a function instead of in the loop like rarity is less efficient but a bit tidier.
#    dungeon_names = getDungeonNames(english)
#    buff_tooltips = getBuffTooltips(english)

    #open the base game trinket file and convert from list to map
    with open(DDpath+'trinkets/base.entries.trinkets.json') as fp:
        temp_baseTrinkets = json.load(fp)
    baseTrinketInfo = {}
    for entry in temp_baseTrinkets['entries']:
        baseTrinketInfo[entry['id']] = entry

    #open the base game buffs file and convert from list to map
    with open(DDpath+'shared/buffs/base.buffs.json') as fp:
        baseBuffs = json.load(fp)
    baseBuffInfo = {}
    for buff in baseBuffs['buffs']:
        baseBuffInfo[buff['id']] = buff

#trinket data: name, rarity, hero_class(if any), origin, effects[list], additional(?), limit, price
    for trinket_id in trinket_dict:
        if trinket_id in baseTrinketInfo:
            d_trinket = trinket_dict[trinket_id]
            s_trinket = baseTrinketInfo[trinket_id]
            #name (done above)
            #rarity
            d_trinket['rarity'] = misc_strings['trinket_rarity_'+s_trinket['rarity']]  #rarity_dict[s_trinket['rarity']]
            #hero_class
            hero = ""
            if len(s_trinket['hero_class_requirements']):
                #TODO I didn't see any trinkets that had multiple hero classes, but there might be in the future.
                hero = hero_dict[s_trinket['hero_class_requirements'][0]]#for now just using the first hero if present
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
                print s_trinket['id']
                for buff_id in s_trinket['buffs']:
                    buff_info = baseBuffInfo[buff_id]
                    rule_id = 'buff_rule_tooltip_' + buff_info['rule_type']
                    stat_str_id = 'buff_stat_tooltip_'+ buff_info['stat_type']
                    if len(buff_info['stat_sub_type']):
                        stat_str_id += '_'+buff_info['stat_sub_type']
                    stat_str = misc_strings[stat_str_id]
                    #print stat_str
                    stat_str = remove_tags(stat_str)
                    amount = float(buff_info['amount'])
                    if amount <1 and amount >-1:
                        amount = amount*100 #workaround for the %fomatter not multiplying as expected
                    stat_str = stat_str % (amount)
                    base_str = misc_strings[rule_id]
                    #print base_str
                    base_str = remove_tags(base_str)
                    print buff_id
                    print stat_str
                    print base_str
                    try:
                        base_str = base_str % (stat_str,buff_info['rule_data']['float'])
                    except TypeError:
                        base_str = base_str % (stat_str)
                    d_trinket['buffs'].append(base_str)

            #trinket_dict[trinket_id] = d_trinket

        else:
            #these trinkets were in the xml, but not in the base trinkets.
            #for example "musketeer" trinkets.
            print trinket_id + " no match"


    #print trinket_dict
    with open(out_dir+'trinkets.json', 'w') as fp:
        json.dump(trinket_dict, fp, indent=4, separators=_separators, sort_keys=True)

#remove tags like '{colour|blight}' from the strings
def remove_tags(string):
    while string.find('{')!=-1 and string.find('}')!=-1:
        string = string.replace(string[string.find('{'):string.find('}')+1],"")
        #print string
    return string

def main():
    parse_trinkets()

if __name__ == "__main__":
    main()




