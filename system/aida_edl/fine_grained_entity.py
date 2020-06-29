# -*- coding: utf-8 -*
import os
import sys
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))


import ujson as json
import argparse
# from event_newtype.fine_grained_events import entity_finegrain_by_json
from aida_utilities.finegrain_util import FineGrainedUtil
# from .geonames_property import get_feature
from collections import defaultdict
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from pymystem3 import Mystem

# from collections import Counter
import numpy as np
from flashtext import KeywordProcessor
import xml.etree.ElementTree as ET
import re

prefix = "https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#"

def load_lemmer(lang):
    if lang.startswith('en'):
        lemmer = WordNetLemmatizer()
        return lemmer
    elif lang.startswith('ru'):
        lemmer = Mystem()
        return lemmer
    elif lang.startswith('uk'):
        stemmer = dict()
        for line in open(os.path.join(CURRENT_DIR, 'conf', 'lemmatization-uk.txt')):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 2:
                stemmer[tabs[0]] = tabs[1]
        return stemmer
    else:
        return None

def lemma_long(trigger, lemmer, lang):
    if lang.startswith('en'):
        return ' '.join([lemmer.lemmatize(trigger_sub) for trigger_sub in trigger.split(' ')])
    elif lang.startswith('ru'):
        return ' '.join(lemmer.lemmatize(trigger))
    elif lang.startswith('uk'):
        toks = []
        for trigger_sub in trigger.split(' '):
            if trigger_sub in lemmer:
                toks.append(lemmer[trigger_sub])
            else:
                toks.append(trigger_sub)
        return ' '.join(toks)
    else:
        return trigger


def stem_long(trigger, stemmer, lang):
    if lang.startswith('uk'):
        toks = []
        for trigger_sub in trigger.split(' '):
            if trigger_sub in stemmer:
                toks.append(stemmer[trigger_sub])
            else:
                toks.append(trigger_sub)
        return ' '.join(toks)
    else:
        return ' '.join([stemmer.stem(trigger_sub) for trigger_sub in trigger.split(' ')])


def load_stemmer(lang):
    if lang.startswith('en'):
        stemmer = SnowballStemmer("english")
        return stemmer
    elif lang.startswith('ru'):
        stemmer = SnowballStemmer("russian")
        return stemmer
    elif lang.startswith('uk'):
        stemmer = dict()
        for line in open(os.path.join(CURRENT_DIR, 'conf', 'lemmatization-uk.txt')):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 2:
                stemmer[tabs[0]] = tabs[1]
        return stemmer
    else:
        return None

def prep_type_old(typestr):
    return typestr.split('#')[-1]

def load_entity_info(entity_coarse):
    # entity_offset = defaultdict(set)
    entity_offset_mention = defaultdict(lambda : defaultdict(str))
    entity_geonames = dict()
    for line in open(entity_coarse):
        line = line.rstrip('\n')
        if line.startswith(':Entity'):
            tabs = line.split('\t')
            entity_id = tabs[0]
            if 'mention' in tabs[1] and 'cannonical_mention' != tabs[1] and 'pronominal_mention' != tabs[1]:
                entity_offset_mention[entity_id][tabs[3]] = tabs[2][1:-1]
            if 'link' == tabs[1]:
                entity_geonames[entity_id] = tabs[2]
    return entity_offset_mention, entity_geonames

def load_type_mapping(mapping_file):
    yago_aida_map = {}
    for line in open(mapping_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        for yago_type in tabs[1].split(','):
            # if yago_type in yago_aida_map:
            #     print('Multiple annotation ', yago_type)
            yago_aida_map[yago_type.strip(' ')] = tabs[0]
    return yago_aida_map

def load_type_mapping_weight(mapping_file):
    yago_aida_map = defaultdict(lambda : defaultdict())
    for line in open(mapping_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        for yago_type in tabs[2].split(','):
            # if yago_type in yago_aida_map:
            #     print('Multiple annotation ', yago_type)
            yago_aida_map[yago_type.strip(' ')][tabs[1]] = float(tabs[0])
    return yago_aida_map

def load_keywords(mapping_file, lang, lemma=True, stemmer=None):
    keywords_aida_map = {}
    for line in open(mapping_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        for keyword in tabs[1].split(','):
            keyword = keyword.strip(' ').lower()
            if lemma:
                # keyword = lemmatizer.lemmatize(keyword)
                keyword = stem_long(keyword, stemmer, lang)
            keywords_aida_map[keyword] = tabs[0]
    return keywords_aida_map

def load_geonames(geonames_mapping_file):
    geocode_aida_map = {}
    for line in open(geonames_mapping_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        geocode_aida_map[tabs[1]] = tabs[0]
    return geocode_aida_map

def load_yago_modeloutput(model_output, lemmer):
    '''
    load fine-grained typing system output
    e.g. HC0007HXR:248-257       Washington      City108524735   0.21216438710689545
    :return:
    '''
    offset_yago_map = dict()
    for line in open(model_output):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        offset = tabs[0]
        mention = tabs[1].lower()
        yago_type = tabs[2]
        # confidence = tabs[3]
        if lemma_long(mention, lemmer, lang) == 'president' \
                or lemma_long(mention, lemmer, lang) == 'президент':
            offset_yago_map[offset] = 'President110467179'
        elif lemma_long(mention, lemmer, lang) == 'government' \
                or lemma_long(mention, lemmer, lang) == 'правительство' \
                or lemma_long(mention, lemmer, lang) == 'уряду':
            offset_yago_map[offset] = 'Government108050678'
        elif (mention == 'woman' or mention == 'women' or mention == 'witnesses' \
                or mention == 'son' or mention == 'relatives' or mention == 'brothers' \
                or mention == 'children' or mention == 'husband' or mention == 'wife' \
                or mention == 'boy' or mention == 'your' or mention == 'child') and \
                (yago_type == 'President110467179' or yago_type == 'Ruler110541229' or yago_type == 'PresidingOfficer110469346'):
            pass
        elif mention == 'idiot' and yago_type == 'Scientist110560637':
            pass
        else:
            offset_yago_map[offset] = yago_type

    return offset_yago_map

def valid_parent(old_type, new_type, backuptype_mapping):
    parent_old = backuptype_mapping[old_type].split('.')[0]
    parent_new = new_type.split('.')[0]
    if parent_old == parent_new:
        return True
    else:
        return False

# change type
def update_type(entity_id, entity_offsets, entity_mentions, entity_geonames,
                old_type, link_yago_types, offset_yago_map,
                yago_aida_mapping, geocode_aida_map, geonames_features,
                keywords_aida_map, backuptype_mapping,
                stemmer,
                hard_parent_type_constraint=True,
                groundtruth_offset_type=None):   # old_types??
    # all_source_voter = Counter()
    all_source_voter = defaultdict(float)
    remaining_yago_types = set()

    # print('\n=====================================\n')
    # print(entity_id, entity_mentions)
    # print('\n')

    mention_size = len(entity_mentions)

    # check ground truth type:
    new_types_by_gt = defaultdict(int)
    for offset in entity_offsets:
        if offset in groundtruth_offset_type:
            aida_type = groundtruth_offset_type[offset]
            if valid_parent(old_type, aida_type, backuptype_mapping):
                # print(offset, aida_type)
                new_types_by_gt[aida_type] += 1
    # if len(new_types_by_gt) > 0:
    #     new_types_by_gt_sorted = sorted(new_types_by_gt.items(), key=lambda x: (len(x[0].split('.')), x[1]),
    #                                        reverse=True)
    #     print('From Ananya: ', new_types_by_gt_sorted)
    #     # print('\n=====================================\n')
    #     # return new_types_by_gt_sorted[0][0]
    #     all_source_voter[new_types_by_gt_sorted[0][0]] += 1
    # (4) keywords
    # new_types_by_keyword = defaultdict(int)
    for ent_mention in entity_mentions:
        ent_mention_stem = stem_long(ent_mention.lower().replace('the ', ''), stemmer, lang)
        for keyword_stem in keywords_aida_map:
            # keyword_stem = stem_long(keyword.lower(), stemmer, lang)
            if ent_mention_stem == keyword_stem:
                aida_type = keywords_aida_map[keyword_stem]
                if valid_parent(old_type, aida_type, backuptype_mapping):
                    # new_types_by_keyword[aida_type] += 1
                    new_types_by_gt[aida_type] += 1
            if ent_mention_stem == 'the opposition':
                newtypes = dict()
                newtypes['SID.Political.Opposition'] = 1.0
                return newtypes
    # new_types_by_keyword_sorted = sorted(new_types_by_keyword.items(), key=lambda x: (len(x[0].split('.')), x[1]),
    new_types_by_keyword_sorted = sorted(new_types_by_gt.items(), key=lambda x: (len(x[0].split('.')), x[1]),
                                         reverse=True)
    # print('keyword-based: ', new_types_by_keyword_sorted)
    if len(new_types_by_keyword_sorted) > 0:
        # all_source_voter[new_types_by_keyword_sorted[0][0]] += 1
        max_type, max_score = new_types_by_keyword_sorted[0]
        for each_type, each_score in new_types_by_keyword_sorted:
            # if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += float(each_score) / float(mention_size)


    # ranking fine-grained types

    # (3) model-based
    new_types_by_model = defaultdict(int)
    for offset in entity_offsets:
        if offset in offset_yago_map:
            yago_type = offset_yago_map[offset]
            if yago_type in yago_aida_mapping:
                for aida_type in yago_aida_mapping[yago_type]:
                    # if hard_parent_type_constraint:
                    if valid_parent(old_type, aida_type, backuptype_mapping):
                        new_types_by_model[aida_type] += yago_aida_mapping[yago_type][aida_type] #1
            else:
                remaining_yago_types.add(yago_type)
        #         print('model-based: other yago_type ', yago_type)
        # else:
        #     print('No model-based type')
    # model-based 不用管粗细粒度的排序，所以先频率为先
    new_types_by_model_sorted = sorted(new_types_by_model.items(), key=lambda x: (x[1], len(x[0].split('.'))),
                                       reverse=True)
    # print('model-based: ', new_types_by_model_sorted)
    if len(new_types_by_model_sorted) > 0:
        # all_source_voter[new_types_by_model_sorted[0][0]] += 1
        max_type, max_score = new_types_by_model_sorted[0]
        for each_type, each_score in new_types_by_model_sorted:
            # if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += 1.0 * float(each_score) / float(mention_size)

    # (2) linking
    new_types_by_linking = defaultdict(int)
    for yago_type in link_yago_types:
        # 向上取，一旦取到就终止，不应该继续！！！！
        # multiple links
        if yago_type in yago_aida_mapping:
            for aida_type in yago_aida_mapping[yago_type]:
                # (6) match coarse type
                # if hard_parent_type_constraint:
                if valid_parent(old_type, aida_type, backuptype_mapping):
                    # if the parent type of new type does not match the old type, trust the coarse type, and do not update
                    new_types_by_linking[aida_type] += yago_aida_mapping[yago_type][aida_type] #1 # * len(aida_type.split('.'))
        else:
            remaining_yago_types.add(yago_type)
            # print('linking-based: other yago_type ', yago_type)
    new_types_by_linking_sorted = sorted(new_types_by_linking.items(), key=lambda x: (len(x[0].split('.')), x[1]), reverse=True)
    # print('linking-based: ', new_types_by_linking_sorted)
    if len(new_types_by_linking_sorted) > 0:
        max_type, max_score = new_types_by_linking_sorted[0]
        for each_type, each_score in new_types_by_linking_sorted:
            if each_type == 'PER.ProfessionalPosition.Spy' and \
                    ('PER.ProfessionalPosition.Spy' not in all_source_voter):
                continue
            if each_type == 'PER.ProfessionalPosition.Scientist' and \
                    ('PER.ProfessionalPosition.Scientist' not in all_source_voter):
                continue
            # if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
            if len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += float(each_score) / float(mention_size) #float(len(link_yago_types)) #

    # (5) geonames
    # if old_type in ['FAC', 'LOC', 'GPE']:
    if entity_id in entity_geonames:
        feature_class, feature_code = get_feature(entity_geonames[entity_id].split('_')[0], geonames_features)
        if feature_class is not None:
            if feature_code in geocode_aida_map:
                newtype = geocode_aida_map[feature_code]
            else:
                newtype = geocode_aida_map[feature_class]
            if valid_parent(old_type, newtype, backuptype_mapping):
                # print('GeoNames-based (', feature_class, feature_code, '): ', newtype)
                all_source_voter[newtype] += 1

    newtypes = dict()
    if len(all_source_voter) == 0:
        newtype = backuptype_mapping[old_type]
        newtypes[newtype] = 1.0
        # print('\nno fine-grained type')
    else:
        # newtype = all_source_voter.most_common(1)[0][0]
        all_source_voter_sorted = sorted(all_source_voter.items(), key=lambda x: (x[1], len(x[0].split('.'))),
                                             reverse=True)
        max_type, max_score = all_source_voter_sorted[0]
        if old_type.startswith('GPE'):
            newtypes[max_type] = max_score
            return newtypes
        new_score_dict = dict()
        for each_type, each_score in all_source_voter_sorted:
            if each_score >= 0: # max_score * 0.35:
                already_in = False
                for each_new_type in newtypes:
                    if each_type in each_new_type:
                        already_in = True
                if not already_in:
                    newtypes[each_type] = np.tanh(0.7 * each_score)
                    new_score_dict[each_type] = each_score
        # print('\nall_source_voter', all_source_voter)
        # print('\nnormalized_voter', new_score_dict)
        # print('\nfinal fine-grained type', newtypes)#all_source_voter.most_common(1))
    # print(old_type, '->', newtype)
    # print('\n=====================================\n')
    # if not valid_parent(old_type, newtype, backuptype_mapping):
    #     print('[ERROR] old type is ignored', old_type, newtype)
    return newtypes


def load_ground_truth_tab(ground_truth_tab_dir):
    offset_type = dict()
    # print(ground_truth_tab_dir)
    for ground_truth_tab in os.listdir(ground_truth_tab_dir):
        for line in open(os.path.join(ground_truth_tab_dir, ground_truth_tab)):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            offset = tabs[3]
            fine_type = tabs[5]
            offset_type[offset] = fine_type
    return offset_type


def rewrite(entity_coarse, output, entity_yagotypes,
            offset_yago_map, yago_aida_mapping, geocode_aida_map, geonames_features,
            keywords_aida_map, backuptype_mapping, stemmer=None,
            ground_truth_tab_dir=None,
            isFiller=False):
    entity_offset_mention, entity_geonames = load_entity_info(entity_coarse)
    if ground_truth_tab_dir is not None:
        groundtruth_offset_type = load_ground_truth_tab(ground_truth_tab_dir)
    else:
        groundtruth_offset_type = None



    f_out = open(output, 'w')
    if not isFiller:
        f_out.write('UIUC_BLENDER\n\n')
    update_count = 0
    # entity_newtype = dict()
    for line in open(entity_coarse):
        if line.startswith(':Entity') or line.startswith(':Filler'):
            if isFiller ^ ('Filler_' in line):
                continue
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if tabs[1] == 'type':
                entity_id = tabs[0]
                # if entity_id in entity_newtype:
                #     newtype = entity_newtype[entity_id]
                # else:
                old_type = prep_type_old(tabs[2])
                if entity_yagotypes is not None:
                    entity_yagotype_each = entity_yagotypes[entity_id]
                else:
                    entity_yagotype_each = None
                newtype_dict = update_type(entity_id,
                                      entity_offset_mention[entity_id].keys(),
                                      entity_offset_mention[entity_id].values(),
                                      entity_geonames,
                                      old_type,
                                      entity_yagotype_each,
                                      offset_yago_map,
                                      yago_aida_mapping,
                                      geocode_aida_map,
                                      geonames_features,
                                      keywords_aida_map,
                                      backuptype_mapping,
                                      stemmer,
                                      hard_parent_type_constraint=True,
                                      groundtruth_offset_type=groundtruth_offset_type)
                for newtype in newtype_dict:
                    if old_type != newtype:
                        update_count += 1
                    write_score = newtype_dict[newtype]
                    if newtype_dict[newtype] >= 1.0:
                        write_score = 1.0
                    f_out.write('%s\ttype\t%s%s\t%.6f\n' % (entity_id.replace(':Filler_', ':Entity_Filler_'), prefix, newtype, write_score))
                continue
            if not tabs[2].startswith(':Entity'):
                f_out.write('%s\n' % line.replace(':Filler_', ':Entity_Filler_'))
    f_out.flush()
    f_out.close()

    return update_count


def get_feature(geoname_id, geonames_features):
    if geoname_id in geonames_features:
        return geonames_features[geoname_id]['feature_class'], geonames_features[geoname_id]['feature_code']
    else:
        # print('no property for geoname id ', geoname_id)
        return None, None


def load_geoname_features(geonames_features):
    geonames_features = json.load(open(geonames_features))
    return geonames_features


def get_all_ltf_offsets(ltf_path):
    offset_dict = dict()
    for file in os.listdir(ltf_path):
        if '._' in file:
            continue
        file = file.replace('.ltf.xml', '')
        offset_dict[file] = dict()
        offset_dict[file]['starts'] = list()
        offset_dict[file]['ends'] = list()
        tree = ET.parse(os.path.join(ltf_path, file + '.ltf.xml'))
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    for token in seg:
                        if token.tag == "TOKEN":
                            offset_dict[file]['starts'].append(token.attrib["start_char"])
                            offset_dict[file]['ends'].append(token.attrib["end_char"])
    return offset_dict


def extract(type_files, rsd_path, ltf_path, outfile, keyword_source, lang, offset_dict):
    entries = []
    count = -1

    for f in type_files:  # gpe_ru.txt, fac_ru.txt, etc.. which contain the nominal keywords in lang
        if '._' in f:
            continue
        enttype = os.path.basename(f).replace('_' + keyword_source + '.txt', '')

        keyword_processor = KeywordProcessor(case_sensitive=True)

        # for each of the keyword files do....

        with open(f, 'r', encoding='utf-8') as keywordsfile:
            try:
                keywordsfull = keywordsfile.read().strip()
            except UnicodeDecodeError:
                # print(f)
                continue
            keywords = keywordsfull.split('\n')
            for k in keywords:
                if k == 'the':
                    continue
                k = re.sub(r'^the\s', '', k)
                k = re.sub(r'^The\s', '', k)
                keyword_processor.add_keyword(k)

            for fil in os.listdir(rsd_path):

                file = os.path.join(rsd_path, fil)
                if os.path.isfile(file) and '._' not in file:  # do not want mac os hidden files..
                    fname = fil.strip().split('.')[0]
                    # the actual extraction happens here:
                    with open(file, 'r', encoding='utf-8') as rsd:
                        text = rsd.read()
                        keywords_found = keyword_processor.extract_keywords(text, span_info=True)
                        # realign with ltf using math, and write output!
                        for keyword in keywords_found:
                            count = count + 1
                            k1 = keyword[1]
                            k2 = keyword[2]
                            st = k1
                            en = k2 - 1
                            if str(st) not in offset_dict[fname.replace('.ltf.xml', '')]['starts']:
                                #                                print('start',fname, st, text[k1-2:k2+2].strip())
                                #                                print(offset_dict[fname.replace('.ltf.xml','')])
                                #                                sys.exit(1)
                                continue
                            if str(en) not in offset_dict[fname.replace('.ltf.xml', '')]['ends']:
                                #                                print('end', fname, en, keyword)
                                #                                sys.exit(1)
                                continue
                            entries.append('ELISA_IE' + '\t' + \
                                           lang.upper() + '_MENTION_' + str(count).zfill(7) + '\t' + \
                                           text[k1:k2].strip() + '\t' + \
                                           fname + ':' + str(st) + '-' + str(en) + '\t' + \
                                           'NIL' + '\t' + \
                                           enttype + '\t' + \
                                           'NOM' + '\t' + \
                                           '1.000')
    with open(outfile, 'w', encoding='utf-8') as o:
        o.write('\n'.join(entries))


if __name__ == '__main__':
    # lang = 'en'
    # entity_finegrain = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.corf.fine.json' % (lang, lang)
    # # entity_finegrain = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.fine.json' % (lang, lang)
    # entity_coarse = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.corf.cs' % (lang, lang)
    # filler_coarse = '/nas/data/m1/lud2/AIDA/dryrun/201905/filler/%s/filler_%s_cleaned.cs' % (lang, lang)
    # # entity_coarse = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.cs' % (lang, lang)
    # output_entity = '/data/m1/lim22/aida2019/dryrun/0322/%s/edl/entity_%s_fine.cs' % (lang, lang)
    # output_filler = '/data/m1/lim22/aida2019/dryrun/0322/%s/edl/filler_%s_fine.cs' % (lang, lang)
    # visualpath = '/data/m1/lim22/aida2019/dryrun/0322/%s/edl/edl_%s_fine.html' % (lang, lang)

    parser = argparse.ArgumentParser()
    parser.add_argument('lang', type=str,
                        help='lang.')
    parser.add_argument('entity_finegrain', type=str,
                        help='entity_finegrain.json')
    parser.add_argument('entity_freebase_tab', type=str,
                        help='entity_freebase_tab')
    parser.add_argument('fine_grain_model_result', type=str,
                        help='fine-grained typing model result')
    parser.add_argument('geonames_features_result', type=str,
                        help='GeoNames feature result')
    parser.add_argument('entity_coarse', type=str,
                        help='entity_coarse')
    parser.add_argument('output_entity', type=str,
                        help='output_entity')
    parser.add_argument('output_filler', type=str,
                        help='output_filler')
    # parser.add_argument('visualpath', type=str,
    #                     help='visualpath')
    parser.add_argument('--filler_coarse', type=str, default="",
                        help='filler_coarse')
    parser.add_argument('--hard_parent_constraint', type=bool, default=True,
                        help='hard_parent_type_constraint')
    parser.add_argument('--ground_truth_tab_dir', type=str,
                        help='ground_truth_tab_dir')
    parser.add_argument('--ltf_dir', type=str, default="",
                        help='ltf_dir')
    parser.add_argument('--rsd_dir', type=str, default="",
                        help='rsd_dir')

    args = parser.parse_args()

    lang = args.lang
    entity_finegrain = args.entity_finegrain
    entity_freebase_tab = args.entity_freebase_tab
    model_output = args.fine_grain_model_result
    geonames_features_result = args.geonames_features_result
    entity_coarse = args.entity_coarse
    filler_coarse = args.filler_coarse
    output_entity = args.output_entity
    output_filler = args.output_filler
    # visualpath = args.visualpath
    hard_parent_type_constraint = args.hard_parent_constraint
    ground_truth_tab_dir = args.ground_truth_tab_dir
    if not os.path.exists(ground_truth_tab_dir):
        os.makedirs(ground_truth_tab_dir, exist_ok=True)

    # generate ground truth file
    offset_dict = get_all_ltf_offsets(args.ltf_dir)
    for keyword_source in ['cleaned', 'ace', 'wiki']:
        filelist = list()
        anno_keywords_dir = os.path.join(CURRENT_DIR, 'conf', 'ldc_anno_keywords')
        for f in os.listdir(anno_keywords_dir):
            for f_2 in os.listdir(os.path.join(anno_keywords_dir, f)):
                filelist.append(os.path.join(anno_keywords_dir, f, f_2))
        extract(filelist, args.rsd_dir, args.ltf_dir,
                os.path.join(ground_truth_tab_dir, 'entities_ldc_%s.txt' % keyword_source),
                keyword_source, args.lang, offset_dict)

    # fine-grained typing
    stemmer = load_stemmer(lang)
    lemmer = load_lemmer(lang)
    mapping_file = os.path.join(CURRENT_DIR, 'conf', 'aida_yago_mapping_weighted.txt')
    mapping_backup_file = os.path.join(CURRENT_DIR, 'conf', 'rename_type.txt')
    geonames_mapping_file = os.path.join(CURRENT_DIR, 'conf', 'geonames_mapping.txt')
    keywords_file = os.path.join(CURRENT_DIR, 'conf', 'keywords.txt')

    hierarchy_dir = os.path.join(CURRENT_DIR, 'conf', 'yago_taxonomy_wordnet_single_parent.json')
    finetype_util = FineGrainedUtil(hierarchy_dir)

    # print('fine-grained types')
    entity_yagotypes = finetype_util.entity_finegrain_by_json(entity_finegrain, entity_freebase_tab, entity_coarse, filler_coarse)
    offset_yago_map = load_yago_modeloutput(model_output, lemmer)
    # print('entity_yagotypes: ', len(entity_yagotypes))
    yago_aida_mapping = load_type_mapping_weight(mapping_file)
    backuptype_mapping = load_type_mapping(mapping_backup_file)
    geocode_aida_map = load_geonames(geonames_mapping_file)
    keywords_aida_map = load_keywords(keywords_file, lang, lemma=True, stemmer=stemmer)
    geonames_features = load_geoname_features(geonames_features_result)

    # entity_newtype = update_type_all(entity_yagotypes, YAGO_AIDA_mapping)

    # print(ground_truth_tab_dir)
    # rewrite(entity_newtype, entity_coarse, output_entity, backuptype_mapping, False, hard_parent_type_constraint)
    update_count = \
        rewrite(entity_coarse, output_entity, entity_yagotypes,
            offset_yago_map, yago_aida_mapping, geocode_aida_map, geonames_features,
            keywords_aida_map, backuptype_mapping, stemmer, ground_truth_tab_dir, False)
    if filler_coarse is not None and len(filler_coarse) != 0:
        # rewrite(entity_newtype, filler_coarse, output_filler, backuptype_mapping, True, hard_parent_type_constraint)
        update_count += \
            rewrite(filler_coarse, output_filler, entity_yagotypes,
                offset_yago_map, yago_aida_mapping, geocode_aida_map, geonames_features,
                keywords_aida_map, backuptype_mapping, stemmer, ground_truth_tab_dir, True)

    # print(update_count)