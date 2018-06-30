#! /usr/bin/python3

import xml.etree.ElementTree as ET
import json
from collections import OrderedDict
import os

import DD_utils


quirk_files = ['dlc/580100_crimson_court/features/crimson_court/shared/quirk/crimson_court.quirk_library.json',
               'dlc/735730_color_of_madness/shared/quirk/com.quirk_library.json',
               'shared/quirk/quirk_library.json']

def parse_quirks():
    misc_strings = DD_utils.getLanguageDict()
    #until all the data is parsed the game_id will be the key, at the end
    #a new dict will be made with the stripped (search) name as the key.
    quirk_dict = {}
    for key in misc_strings:
        if key.startswith('str_quirk_name_'):
            q_id = key.replace('str_quirk_name_', "")
            q_name = misc_strings[key]
            quirk_dict[q_id] = {'name': q_name, 'id': q_id }

    #load all of the trinket info files
    quirkInfos = DD_utils.loadInfoFiles(quirk_files, 'quirks')
    #load all of the buff files
    buffInfos = DD_utils.getBuffInfos()

#quirk data: name, positive/negative, is disease, buffs
    skipped_quirks = []
    for quirk_id in quirk_dict:
        if quirk_id in quirkInfos:
            quirk_out = quirk_dict[quirk_id]
            quirk_in = quirkInfos[quirk_id]

            quirk_out['is_positive'] = quirk_in['is_positive']
            quirk_out['is_disease'] = quirk_in['is_disease']
            if quirk_in['is_disease'] == True:
                quirk_out['quirk_type'] = 'Disease'
            elif quirk_in['is_positive'] == True:
                quirk_out['quirk_type'] = 'Positive'
            else:
                quirk_out['quirk_type'] = 'Negative'
            if quirk_in['is_disease'] == True and quirk_in['is_positive'] == True:
                    print("WARNING found disease marked as positive")

            #effects
            #TODO I think all this buff parsing can move to a util function.
            #create a list of effects as strings.
            if len(quirk_in['buffs']):
                buffList = []
                for buff_id in quirk_in['buffs']:
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
                        print ('WARNING: {} may have parsed incorrectly : {}'.format(quirk_out['id'], stat_str))
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
                quirk_out['buffs'] = list(OrderedDict.fromkeys(buffList))

        else:
            #these quirks were in the xml, but not found in trinket info
            print (quirk_id + " no match")
            skipped_quirks.append(quirk_id)

    #remove any trinkets that had a name but no info
    for quirk_id in skipped_quirks:
        del quirk_dict[quirk_id]

    #change key to the stripped name
    quirk_output = {}
    for key in quirk_dict:
        quirk_output[DD_utils.stripName(quirk_dict[key]['name'])] = quirk_dict[key]

    with open(DD_utils.out_dir+'quirks.json', 'w') as fp:
        json.dump(quirk_output, fp, indent=4, separators=DD_utils.separators, sort_keys=True)

#main
def main():
    parse_quirks()

if __name__ == "__main__":
    main()

