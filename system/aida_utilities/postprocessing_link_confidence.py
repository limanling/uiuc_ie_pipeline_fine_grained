from collections import defaultdict
import numpy as np
import os
import sys
import ujson as json
import argparse
# from sklearn import preprocessing

parser = argparse.ArgumentParser()
# parser.add_argument('language_id', type=str, help='lang.')
parser.add_argument('linking_multiple_json', type=str, help='%s.linking.tab.candidates.json')
parser.add_argument('input_cs', type=str, help='input cold start')
# parser.add_argument('result_path', default=str, help='result_path')
parser.add_argument('output_cs', type=str, help='output cold start')
parser.add_argument('out_link_private_data', default=str, help='%s/edl/lorelei_private_data.json')
args = parser.parse_args()

top_n = 3

# language_id = args.language_id
# lang = language_id.split('_')[0]
# fine_grained_path = "/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0327%s/" % (lang, language_id.replace(lang, ""))
# linking_multiple_json= os.path.join(fine_grained_path, '%s.linking.tab.candidates.json' % lang) ##Xiaoman's
# final_cs = os.path.join(result_path, '%s/%s_full_sponsor_coref_clean.cs' % (language_id, language_id))
# final_cs = os.path.join(result_path, '%s/%s_full.cs' % (language_id, language_id))
# out_full_cs_link = os.path.join(result_path, '%s/%s_full_link.cs' % (language_id, language_id))
# result_path = '/data/m1/lim22/aida2019/dryrun/0510'
# out_link_max = os.path.join(result_path, '%s/edl/lorelei_private_data.json' % (language_id))
linking_multiple_json = args.linking_multiple_json
final_cs = args.input_cs
out_full_cs_link = args.output_cs
out_link_max = args.out_link_private_data

norm_max = 1.0
norm_min = 0.2

# LDC2018E80_ids_file = "/nas/data/m1/AIDA_Data/LDC_raw_data/LDC2019E43_AIDA_Phase_1_Evaluation_Reference_Knowledge_Base/data/__entities_geo.ids.txt"
# LDC2018E80_ids = set()
# for line in open(LDC2018E80_ids_file):
#     LDC2018E80_ids.add(line.rstrip('\n'))

offset_link = json.load(open(linking_multiple_json)) # offset -> array([link, confidence])
# linking_multiple_tab
# offset_link = defaultdict(lambda: defaultdict(float))
# for line in open(linking_tab):
#     line = line.rstrip('\n')
#     tabs = line.split('\t')
#     offset = tabs[3]
#     link = tabs[4]
#     if not link.startswith('NIL'):
#         confidence = float(tabs[7])
#         offset_link[offset][link] = confidence

print('total offsets ', len(offset_link))
# edl_cs
entity_offset_mapping = defaultdict(list)
# confidence_dict = defaultdict(lambda: defaultdict(list))
confidence_dict_sum = defaultdict(lambda: defaultdict(float))
confidence_dict_max = defaultdict(lambda: defaultdict(float))
confidence_dict_count = defaultdict(lambda: defaultdict(float))
# confidence_dict = defaultdict(lambda: defaultdict(float))
# confidence_num = defaultdict(int)
for line in open(final_cs):
    line = line.rstrip('\n')
    if line.startswith(':Entity') and 'Filler_' not in line:
        tabs = line.split('\t')
        if 'mention' == tabs[1]:
            entity_id = tabs[0]
            offset = tabs[3]
            entity_offset_mapping[entity_id].append(offset)
            if offset in offset_link:
                link_count = 0
                for linking_result in offset_link[offset]:
                    if link_count < top_n:
                        # if linking_result[0] in LDC2018E80_ids:
                        link_count += 1
                        link_name = 'LDC2019E43:%s' % (linking_result[0])
                        # else:
                        #     link_name = 'GeoUpdate:%s' % (linking_result[0])
                        confidence_dict_sum[entity_id][link_name] += linking_result[1]
                        confidence_dict_count[entity_id][link_name] += 1.0
                        if linking_result[1] > confidence_dict_max[entity_id][link_name]:
                            confidence_dict_max[entity_id][link_name] = linking_result[1]
                    else:
                        break
            else:
                print('No Link ', offset)

del offset_link

print('Start sorting...')

kb_link_avg_norm = defaultdict(lambda: defaultdict(float))
kb_link_max = defaultdict(lambda: defaultdict(float))
for entity_id in confidence_dict_sum:
    # max-pool
    for offset in entity_offset_mapping[entity_id]:
        kb_link_max[offset] = confidence_dict_max[entity_id]
    # avg-pool
    max_kb_link, max_kb_link_score = sorted(confidence_dict_sum[entity_id].items(), key=lambda x:x[1], reverse=True)[0]
    # norm_ratio = 1.0 / max_kb_link_score
    for kb_link in confidence_dict_sum[entity_id]:
        if confidence_dict_count[entity_id][kb_link] < 0.2 * confidence_dict_count[entity_id][max_kb_link]:
            continue
        # kb_link_avg_norm[entity_id][kb_link] = confidence_dict_sum[entity_id][kb_link] * norm_ratio
        kb_link_avg_norm[entity_id][kb_link] = confidence_dict_sum[entity_id][kb_link] / confidence_dict_count[entity_id][kb_link]

writer = open(out_full_cs_link, 'w')
for line in open(final_cs):
    line = line.rstrip('\n')
    tabs = line.split('\t')
    if len(tabs) > 2:
        if 'link' == tabs[1]:
            entity_id = tabs[0]
            for kb_link in kb_link_avg_norm[entity_id]:
                # if kb_link in LDC2018E80_ids:
                #     link_pre = 'LDC2018E80'
                # else:
                #     link_pre = 'GeoUpdate'
                # writer.write(('%s\tlink\t%s:%s\t%.4f\n' % (tabs[0], link_pre, kb_link, kb_link_avg_norm[entity_id][kb_link]))
                #              .replace("0.0000", "0.0010"))
                if kb_link_avg_norm[entity_id][kb_link] < 0.1:
                    continue
                writer.write(
                    ('%s\tlink\t%s\t%.4f\n' % (tabs[0], kb_link, kb_link_avg_norm[entity_id][kb_link]))
                    .replace("0.0000", "0.0010"))
                writer.flush()
            continue
    writer.write('%s\n' % line)
writer.flush()
writer.close()

json.dump(kb_link_max, open(out_link_max, 'w'), indent=4)

print('NIL clustering is deleted')