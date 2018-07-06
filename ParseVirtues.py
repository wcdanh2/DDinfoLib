#! /usr/bin/python3

import xml.etree.ElementTree as ET
import json
from collections import OrderedDict
import os

import DD_utils

#"traits" appears to be the generic name that encompases afflictions and virtues
#This parser will get both afflictions and virtues, but place them into the virtues.json
#file since it is a bit more memorable than traits.
virtue_files = ['shared/trait/trait_library.json']

def parse_virtues():
    misc_strings = DD_utils.getLanguageDict()
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    virtue_dict = {}
    for key in misc_strings:
        if key.startswith('str_virtue_name_'):
            q_id = key.replace('str_virtue_name_', "")
            q_name = misc_strings[key]
            virtue_dict[q_id] = {'name': q_name, 'id': q_id }
        elif key.startswith('str_affliction_name_'):
            q_id = key.replace('str_affliction_name_', "")
            q_name = misc_strings[key]
            virtue_dict[q_id] = {'name': q_name, 'id': q_id }

    #load all of the trinket info files
    virtueInfos = DD_utils.loadInfoFiles(virtue_files, 'traits')
    #load all of the buff files
    buffInfos = DD_utils.getBuffInfos()

#virtue data: name, positive/negative, is disease, buffs
    skipped_virtues = []
    for virtue_id in virtue_dict:
        if virtue_id in virtueInfos:
            virtue_out = virtue_dict[virtue_id]
            virtue_in = virtueInfos[virtue_id]


            #effects
            #TODO I think all this buff parsing can move to a util function.
            #create a list of effects as strings.
            if len(virtue_in['buff_ids']):
                buffList = []
                for buff_id in virtue_in['buff_ids']:
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
                        print ('WARNING: {} may have parsed incorrectly : {}'.format(virtue_out['id'], stat_str))
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
                virtue_out['buffs'] = list(OrderedDict.fromkeys(buffList))

            #dialogue
            #"overstress_type": "affliction",
            if virtue_in['overstress_type'] == "virtue":
                virtue_out['dialogue'] = misc_strings['str_virtue_description_'+virtue_id]
            elif virtue_in['overstress_type'] == "affliction":
                #virtue_out['dialogue'] = misc_strings['str_affliction_description_'+virtue_id]
                #the description in the string files isn't actually what we want so build it manually.
                dialogue = ""
                for buff in virtue_out['buffs']:
                    if 'Resist' not in buff and 'Disarm' not in buff:
                        if len(dialogue):
                            dialogue += ", "
                        dialogue += buff
                virtue_out['dialogue'] = dialogue
            else:
                print("Could not find description sting for: {}".format(virtue_id))

        else:
            #these virtues were in the xml, but not found in trinket info
            print (virtue_id + " no match")
            skipped_virtues.append(virtue_id)

    #remove any trinkets that had a name but no info
    for virtue_id in skipped_virtues:
        del virtue_dict[virtue_id]

    #change key to the stripped name
    virtue_output = {}
    for key in virtue_dict:
        virtue_output[DD_utils.stripName(virtue_dict[key]['name'])] = virtue_dict[key]

    with open(DD_utils.out_dir+'virtues.json', 'w') as fp:
        json.dump(virtue_output, fp, indent=4, separators=DD_utils.separators, sort_keys=True)

#main
def main():
    parse_virtues()

if __name__ == "__main__":
    main()

