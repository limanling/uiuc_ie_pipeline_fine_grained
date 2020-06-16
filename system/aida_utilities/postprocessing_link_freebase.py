from collections import defaultdict
import numpy as np
import ujson as json
import os
import sys
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    # parser.add_argument('language_id', type=str, help='lang.')
    parser.add_argument('freebase_tab', type=str, help='%s.linking.freebase.tab')
    parser.add_argument('input_cs', type=str, help='input cold start')
    # parser.add_argument('result_path', default=str, help='result_path')
    parser.add_argument('out_freebase_private_data', default=str, help='%s/edl/freebase_private_data.json')
    args = parser.parse_args()

    # language_id = args.language_id
    # lang = language_id.split('_')[0]
    # fine_grained_path = "/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0430%s/" % (lang, language_id.replace(lang, ""))
    # result_path = '/data/m1/lim22/aida2019/dryrun/0510'
    # freebase_tab = os.path.join(fine_grained_path, '%s.linking.freebase.tab' % lang)
    # edl_cs = os.path.join(result_path, '%s/%s_full.cs' % (language_id, language_id))
    # out_freebase = os.path.join(result_path, '%s/edl/freebase_private_data.json' % (language_id))
    freebase_tab = args.freebase_tab
    edl_cs = args.input_cs
    out_freebase = args.out_freebase_private_data

    # edl_cs='/data/m1/lim22/aida2019/dryrun/0430/en/en_full.cs'
    # freebase_tab='/nas/data/m1/panx2/tmp/aida/eval/2019/en/0430/en.linking.freebase.tab'
    # out_freebase = '/data/m1/lim22/aida2019/dryrun/0430/en/edl/freebase_private_data.json'
    # out_freebase_max = '/data/m1/lim22/aida2019/dryrun/0430/en/edl/freebase_private_data_max.json'

    # freebase_tab
    offset_link = defaultdict(lambda : defaultdict(float))
    for line in open(freebase_tab):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        offset = tabs[3]
        link = tabs[4]
        if not link.startswith('NIL'):
            confidence = float(tabs[7])
            offset_link[offset][link] = confidence


    # edl_cs
    entity_offset_mapping = defaultdict(list)
    confidence_dict = defaultdict(lambda : defaultdict(list))
    for line in open(edl_cs):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        if line.startswith(':Entity') and 'mention' in tabs[1]:
            entity_id = tabs[0]
            offset = tabs[3]
            entity_offset_mapping[entity_id].append(offset)
            for freebase_link in offset_link[offset]:
                confidence = offset_link[offset][freebase_link]
                confidence_dict[entity_id][freebase_link].append(confidence)

    freebase_link_map = defaultdict(lambda : defaultdict(lambda : defaultdict(float)))
    # freebase_link_max = defaultdict(lambda : defaultdict(float))
    for entity_id in confidence_dict:
        for freebase_link in confidence_dict[entity_id]:
            mean = np.mean(confidence_dict[entity_id][freebase_link])
            max = np.max(confidence_dict[entity_id][freebase_link])
            # freebase_link_mean[entity_id][freebase_link] = mean
            for offset in entity_offset_mapping[entity_id]:
                freebase_link_map[offset][freebase_link]['average_score'] = mean
                freebase_link_map[offset][freebase_link]['max_score'] = max

    # for offset in freebase_link_mean:
    #     freebase_link_mean[offset] = sorted(freebase_link_mean[offset].items(), key=lambda x:x[1], reverse=True)

    json.dump(freebase_link_map, open(out_freebase, 'w'), indent=4)
    # json.dump(freebase_link_max, open(out_freebase_max, 'w'), indent=4)

    ## next step: assign different scores for each document

    # freebase_link = freebase_link_map['HC000Q7M8:1868-1871']
    # print(freebase_link)
    # linking_info = sorted(freebase_link.items(), key=lambda x: x[1]['average_score'], reverse=True)[0][0]
    # print(linking_info)

    # "HC000Q7M8:1868-1871": {
    #     "m.059dn": {
    #         "average_score": 0.199,
    #         "max_score": 0.559
    #     },
    #     "m.02vnt5x": {
    #         "average_score": 0.25,
    #         "max_score": 0.25
    #     },
    #     "m.01bl19": {
    #         "average_score": 0.163,
    #         "max_score": 0.163
    #     }
    # },