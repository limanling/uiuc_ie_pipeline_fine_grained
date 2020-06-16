import argparse
import ujson as json
from collections import defaultdict
import os
import sys
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from aida_utilities.ltf_util import LTF_util
import numpy as np


def gen_confidence(langsource, linking_tab, linking_multiple_json, final_cs, ltf_dir, output_conf_all):
    nom_conf = 0.2
    pro_conf = 0.1
    nil_conf = 0.7

    named_entity = set()
    nom_entity = set()

    offset_link = json.load(open(linking_multiple_json))  # offset -> array([link, confidence])

    writer_all_conf = open(output_conf_all, 'w')
    for docid in os.listdir(ltf_dir):
        if not docid.endswith('.ltf.xml'):
            continue
        docid = docid.replace('.ltf.xml', '')
        offset_mentionconf = dict()
        for file in files:
            for line in open(file):
                line = line.rstrip('\n')
                tabs = line.split('\t')
                if docid in tabs[3]:
                    # mention_name = tabs[2]
                    offset = tabs[3]
                    mention_conf = float(tabs[-1])
                    offset_mentionconf[offset] = mention_conf

        # offset_link = json.load(open(linking_multiple_json)) # offset -> array([link, confidence])
        offset_linkingconf = dict()
        for line in open(linking_tab):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if docid in tabs[3]:
                # mention_name = tabs[2]
                offset = tabs[3]
                mention_type = tabs[6]
                # print(tabs[-1])
                # linking_conf = float(tabs[7])
                if mention_type == 'NOM':
                    offset_linkingconf[offset] = nom_conf  # linking_conf * nom_conf
                elif mention_type == 'PRO':
                    offset_linkingconf[offset] = pro_conf  # linking_conf * pro_conf
                elif 'asr' in docid or 'ocr' in docid or 'asr' in langsource or 'ocr' in langsource:
                    offset_linkingconf[offset] = 0.1
                else:
                    if offset in offset_link and len(offset_link[offset]) != 0:
                        _, offset_linkingconf[offset] = offset_link[offset][0]
                    else:
                        offset_linkingconf[offset] = nil_conf  # NIL clustering ??? (no confidence)
                    # offset_linkingconf[offset] = linking_conf * (1.0-nom_conf) + nom_conf

        ltf_util = LTF_util(ltf_dir)
        entity_str = defaultdict(list)
        entity_scores = defaultdict(float)
        entity_counts = defaultdict(float)
        entity_infor = defaultdict(lambda: defaultdict(str))
        # writer = open(os.path.join(output_dir, docid+'.html'), 'w')
        for line in open(final_cs):
            line = line.rstrip('\n')
            if line.startswith(':Entity'):
                tabs = line.split('\t')
                entity_id = tabs[0]
                if 'type' in tabs[1]:
                    entity_type = tabs[2].split('#')[-1]
                elif 'canonical_mention' in tabs[1] and docid in tabs[3]:
                    info_mention_offset = tabs[3]
                    info_doc_id = info_mention_offset.split(':')[0]
                    entity_infor[info_doc_id][tabs[0]] = info_mention_offset
                    # offset = tabs[3]
                    # if offset not in offset_mentionconf or offset not in offset_linkingconf:
                    #     continue
                    # mention_conf = offset_mentionconf[offset]
                    # link_conf = offset_linkingconf[offset]
                    # writer.write('[Informative Mention]: %s\t\t%s\t\t%s\t\t%0.2f\t\t%0.2f\n' %
                    #              (entity_id, entity_type, info_mention, mention_conf, link_conf))
                    # entity_str[entity_id].append('[Informative Mention]: %s\t\t%s\t\t%s\t\t%0.2f\t\t%0.2f' %
                    #              (entity_id, entity_type, info_mention, mention_conf, link_conf))
                elif 'mention' in tabs[1] and docid in tabs[3]:
                    offset = tabs[3]
                    if offset not in offset_mentionconf or offset not in offset_linkingconf:
                        continue
                    if 'mention' == tabs[1]:
                        named_entity.add(entity_id)
                    if 'nominal_mention' == tabs[1]:
                        nom_entity.add(entity_id)
                    mention_name = tabs[2]
                    mention_conf = offset_mentionconf[offset]
                    link_conf = offset_linkingconf[offset]
                    entity_scores[entity_id] += mention_conf * link_conf
                    entity_counts[entity_id] += 1.0
                    # entity_str[entity_id].append('%s\t\t%s\t\t%s\t\t%0.2f\t\t%0.2f\t\t\n<br>%s' %
                    #              (entity_id, entity_type, mention_name, mention_conf, link_conf, ltf_util.get_context_html(offset)))

        for entity_id in entity_scores:
            score = entity_scores[entity_id]
            # average
            # entity_scores[entity_id] = entity_scores[entity_id] / entity_counts[entity_id]
            # normalize
            entity_scores[entity_id] = np.tanh(2.7 * score)  # np.tanh(0.5 * score) #(score - min_score) / norm_ratio
            if entity_scores[entity_id] < 0.001:
                entity_scores[entity_id] = 0.001
            if entity_scores[entity_id] > 0.95:
                entity_scores[entity_id] = 1.0
            if entity_id not in named_entity:
                if entity_id in nom_entity:
                    entity_scores[entity_id] = entity_scores[entity_id] * nom_conf
                else:
                    entity_scores[entity_id] = entity_scores[entity_id] * pro_conf
                    entity_scores[entity_id] = entity_scores[entity_id] / entity_counts[entity_id]

        # get the sorted list of mentions (only useful for visualization)
        for entity_id in entity_scores:
            entity_str[entity_id] = sorted(entity_str[entity_id],
                                           key=lambda x: float(x.split('\t\t')[3]) * float(x.split('\t\t')[4]),
                                           reverse=True)

        entity_scores_sorted = sorted(entity_scores.items(), key=lambda x: x[1], reverse=True)
        for entity_id, entity_score in entity_scores_sorted:
            writer_all_conf.write(
                '%s\t%s\t%s\t%6f\n' % (entity_infor[docid][entity_id], docid, entity_id, entity_score))
        #     writer.write('%s: %s, %.4f\n<br>' % (entity_id, entity_infor[entity_id], entity_score))
        #     writer.write('\n<br>'.join(entity_str[entity_id]))
        #     writer.write('\n<br>\n<br>\n<br>')
        #
        #
        # writer.flush()
        # writer.close()
    writer_all_conf.flush()
    writer_all_conf.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('langsource', type=str, help='langsource')
    parser.add_argument('name_mention_tab', type=str, help='%s.nam.tagged.pp.tab')
    parser.add_argument('nom_mention_tab', type=str, help='%s.nom.tagged.tab')
    parser.add_argument('pro_mention_tab', type=str, help='%s.pro.tagged.tab')
    parser.add_argument('linking_tab', type=str, help='en.linking.tab')
    parser.add_argument('linking_multiple_json', type=str, help='en.linking.tab.candidates.json')
    parser.add_argument('ltf_dir', type=str, help='ltf_dir')
    # parser.add_argument('final_cs', type=str, help='entity_filler_fine.cs')
    parser.add_argument('input_cs', type=str, help='input cold start')
    parser.add_argument('output_cs', type=str, help='output cold start')
    parser.add_argument('conf_all', type=str, help='output cold start')

    args = parser.parse_args()

    nom_conf = 0.3
    pro_conf = 0.1

    langsource = args.langsource
    input_cs = args.input_cs
    output_cs = args.output_cs
    name_mention_tab = args.name_mention_tab
    nom_mention_tab = args.nom_mention_tab
    pro_mention_tab = args.pro_mention_tab
    conf_all = args.conf_all
    linking_tab = args.linking_tab
    linking_multiple_json = args.linking_multiple_json
    ltf_dir = args.ltf_dir
    files = [name_mention_tab, nom_mention_tab, pro_mention_tab]

    gen_confidence(langsource, linking_tab, linking_multiple_json, input_cs, ltf_dir, conf_all)

    offset_mentionconf = dict()
    for file in files:
        if not os.path.exists(file):
            print('No file ', file)
            continue
        for line in open(file):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            offset = tabs[3]
            mention_conf = float(tabs[-1])
            if 'NOM' == tabs[6]:
                mention_conf = mention_conf * nom_conf
            elif 'PRO' == tabs[6]:
                mention_conf = mention_conf * pro_conf
            offset_mentionconf[offset] = mention_conf
    # print(offset_mentionconf)

    # entity_maxconf = defaultdict(lambda : defaultdict(float))
    # for line in open(input_cs):
    #     line = line.rstrip('\n')
    #     if line.startswith(':Entity'):
    #         tabs = line.split('\t')
    #         if 'mention' in tabs[1] and 'canonical_mention' not in tabs[1]:
    #        b     entity_id = tabs[0]
    #             offset = tabs[3]
    #             docid = offset[:offset.find(':')]
    #             if offset in offset_mentionconf:
    #                 if offset_mentionconf[offset] > entity_maxconf[entity_id][docid]:
    #                     entity_maxconf[entity_id][docid] = offset_mentionconf[offset]
    doc_ent_conf = defaultdict(lambda : defaultdict(str))
    for line in open(conf_all):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        offset = tabs[0]
        docid = tabs[1]
        entity = tabs[2]
        conf = tabs[3]
        doc_ent_conf[docid][entity] = conf

    writer = open(output_cs, 'w')
    for line in open(input_cs):
        line = line.rstrip('\n')
        if line.startswith(':Entity'):
            tabs = line.split('\t')
            if 'canonical_mention' in tabs[1]:
                entity_id = tabs[0]
                offset = tabs[3]
                docid = offset[:offset.find(':')]
                # if entity_id in entity_maxconf:
                #     mention_conf = entity_maxconf[entity_id][docid]
                #     tabs[4] = '%0.6f' % mention_conf
                #     writer.write('%s\n' % '\t'.join(tabs))
                #     continue
                if entity_id in doc_ent_conf[docid]:
                    tabs[4] = doc_ent_conf[docid][entity_id]
                    writer.write('%s\n' % '\t'.join(tabs))
                    continue
                else:
                    tabs[4] = '%0.6f' % 0.10
                    writer.write('%s\n' % '\t'.join(tabs))
                    continue
            elif 'mention' in tabs[1]:
                offset = tabs[3]
                if offset in offset_mentionconf:
                    mention_conf = offset_mentionconf[offset]
                    # if 'nominal_mention' == tabs[1]:
                    #     mention_conf = mention_conf * nom_conf
                    # elif 'pronominal_mention' == tabs[1]:
                    #     mention_conf = mention_conf * pro_conf
                    tabs[4] = '%0.6f' % mention_conf
                    writer.write('%s\n' % '\t'.join(tabs))
                    continue
        writer.write('%s\n' % line)
    writer.flush()
    writer.close()