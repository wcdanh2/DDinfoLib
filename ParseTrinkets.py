#! /usr/bin/python3

import xml.etree.ElementTree as ET
import json
from collections import OrderedDict

import DD_utils






trinketInfoFiles = ['trinkets/base.entries.trinkets.json',
    'dlc/445700_musketeer/trinkets/musketeer.entries.trinkets.json',
    'dlc/580100_crimson_court/features/crimson_court/trinkets/crimson_court.entries.trinkets.json',
    'dlc/580100_crimson_court/features/flagellant/trinkets/flagellant.entries.trinkets.json',
    'dlc/702540_shieldbreaker/trinkets/shieldbreaker.entries.trinkets.json',
    'dlc/735730_color_of_madness/trinkets/com.entries.trinkets.json',
    'dlc/735730_color_of_madness/trinkets/special_com.entries.trinkets.json']

def parse_trinkets():

    misc_strings = DD_utils.getLanguageDict()
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    trinket_dict = {}
    for key in misc_strings:
        if key.startswith('str_inventory_title_trinket'):
            t_id = key.replace('str_inventory_title_trinket', "")
            t_name = misc_strings[key]
            trinket_dict[t_id] = {'name': t_name, 'id': t_id }

    #load all of the trinket info files
    trinketInfos = DD_utils.loadInfoFiles(trinketInfoFiles, 'entries')
    #load all of the buff files
    buffInfos = DD_utils.getBuffInfos()

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
                buffList = []
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
                    stat_str = DD_utils.remove_tags(stat_str)
                    amount = float(buff_info['amount'])
                    if amount <1 and amount >-1:
                        amount = amount*100 #workaround for the %fomatter not multiplying as expected
                    try:
                        stat_str = stat_str % (amount)
                    except:
                        print ('WARNING: {} may have parsed incorrectly : {}'.format(s_trinket['id'], stat_str))
                    base_str = misc_strings[rule_id]
                    #print base_str
                    base_str = DD_utils.remove_tags(base_str)
                    #print buff_id
                    #print stat_str
                    #print base_str
                    try:
                        if len(buff_info['rule_data']['string']):
                            string2 = misc_strings['buff_rule_data_tooltip_'+buff_info['rule_data']['string']]
                            base_str = base_str % (stat_str, string2)
                        else:
                            num = float(buff_info['rule_data']['float'])
                            if num <1 and num >-1:
                                num=num*100
                            base_str = base_str % (stat_str,num)
                    except TypeError:
                        base_str = base_str % (stat_str)
                    buffList.append(base_str)
                #remove duplicate buffs and add them to the trinket
                d_trinket['buffs'] = list(OrderedDict.fromkeys(buffList))
        else:
            #these trinkets were in the xml, but not found in trinket info
            print (trinket_id + " no match")
            skipped_trinkets.append(trinket_id)

    #remove any trinkets that had a name but no info
    for trinket_id in skipped_trinkets:
        del trinket_dict[trinket_id]

    #change key to the stripped name
    trinket_output = {}
    for key in trinket_dict:
        trinket_output[DD_utils.stripName(trinket_dict[key]['name'])] = trinket_dict[key]

    #print "{} trinkets added to library".format(len(trinket_output))
    with open(DD_utils.out_dir+'trinkets.json', 'w') as fp:
        json.dump(trinket_output, fp, indent=4, separators=DD_utils.separators, sort_keys=True)

#main
def main():
    parse_trinkets()

if __name__ == "__main__":
    main()




