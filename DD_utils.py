#A place to put functions that will be reused by multiple parsers.


import xml.etree.ElementTree as ET
import json

#TODO eventually I would like these paths to be in a config file
#of their own.
DDpath = 'DarkestDungeon/'
out_dir = 'DDinfoLib/'

separators = (',', ': ')

#load the misccellaneous strings and return it as a dict of key(id):text pairs.
string_tables = ['localization/miscellaneous.string_table.xml',
                 'localization/heroes.string_table.xml',
                 'localization/backertrinkets.string_table.xml',
                 'localization/PSN.string_table.xml',
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


#load the buff-info json files and return them as one dictionary.
# the key will be the buff id, and the value will be the same as it's
# list entry in the json file it came from.
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
