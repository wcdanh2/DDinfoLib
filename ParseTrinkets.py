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
        print line.attrib
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

def parse_trinkets():

    tree = ET.parse(DDpath+'localization/miscellaneous.string_table.xml')

    #gets the root of the tree. Idk some weird xml thing
    root = tree.getroot()

    #print root[0].tag
    #I am only interested in english, so lets simplify and get a dict with just the english info.
    english = root[0]

    #print english[0].attrib['id']

    #prints all of the trinket names and adds them to the trinket dict
    #until all the data is parse the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    trinket_dict = {}
    rarity_dict = {}
    for line in english:
        if line.attrib['id'].startswith('str_inventory_title_trinket'):
            #print line.text
            t_id = line.attrib['id'].replace('str_inventory_title_trinket', "")
            t_name = line.text
            trinket_dict[t_id] = {'name': t_name }
        elif line.attrib['id'].startswith('trinket_rarity_'):
            rarity_key = line.attrib['id'].replace('trinket_rarity_', "")
            rarity_dict[rarity_key] = line.text

    hero_dict = getHeroNames()
    #making the dungeon names in a function instead of in the loop like rarity is less efficient but a bit tidier.
    dungeon_names = getDungeonNames(english)
    buff_tooltips = getBuffTooltips(english)

    with open(DDpath+'trinkets/base.entries.trinkets.json') as fp:
        temp_baseTrinkets = json.load(fp)
    #convert from list to dict to make lookup easier.
    baseTrinketInfo = {}
    for entry in temp_baseTrinkets['entries']:
        baseTrinketInfo[entry['id']] = entry

    with open(DDpath+'shared/buffs/base.buffs.json') as fp:
        baseBuffs = json.load(fp)
#trinket data: name, rarity, hero_class(if any), origin, effects[list], additional(?), limit, price
    for trinket_id in trinket_dict:
        if trinket_id in baseTrinketInfo:
            d_trinket = {}
            s_trinket = baseTrinketInfo[trinket_id]
            #name (done above)
            #rarity
            d_trinket['rarity'] = rarity_dict[s_trinket['rarity']]
            #hero_class
            hero = ""
            if len(s_trinket['hero_class_requirements']):
                #TODO I didn't see any trinkets that had multiple hero classes, but there might be in the future.
                hero = hero_dict[s_trinket['hero_class_requirements'][0]]
            d_trinket['hero_class'] = hero
            #origin
            origin = ""
            if len(s_trinket['origin_dungeon']):
                origin = dungeon_names[s_trinket['origin_dungeon']]
            d_trinket['origin_dungeon'] = origin
            #effects
            #create a list of effects as strings.

            trinket_dict[trinket_id] = d_trinket

        else:
            #these may be trinkets that aren't in the game, since their names werent in the xml.
            #or maybe they are in a different xml.. we'll see.
            print trinket_id + " no match"

    print trinket_dict
    with open(out_dir+'trinkets.json', 'w') as fp:
        json.dump(trinket_dict, fp, indent=4, separators=_separators, sort_keys=True)



def main():
    parse_trinkets()

if __name__ == "__main__":
    main()




