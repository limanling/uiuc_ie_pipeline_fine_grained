from rdflib import Graph, plugin, URIRef, Namespace
from aida_interchange import aifutils

import os
import ujson as json
import traceback
import argparse
from collections import defaultdict
import numpy as np

from elmoformanylangs import Embedder
import xml.etree.ElementTree as ET
# import uuid
import base64
# from Crypto.Cipher import AES
# from postprocessing_rename_turtle import load_doc_root_mapping


def load_doc_root_mapping(parent_child_tab_path, child_column_idx, parent_column_idx):
    doc_id_to_root_dict = dict()

    f = open(parent_child_tab_path)
    f.readline()

    for one_line in f:
        one_line = one_line.strip()
        one_line_list = one_line.split('\t')
        doc_id = one_line_list[child_column_idx]  #[3] # uid
        # doc_id = one_line_list[2] # child_uid
        root_id = one_line_list[parent_column_idx]  #[2] # parent_uid
        # root_id = one_line_list[7] # parent_uid
        doc_id_to_root_dict[doc_id] = root_id
    return doc_id_to_root_dict


AIDA = Namespace('https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/InterchangeOntology#')
RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
LDC = Namespace('https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#')
secret_key = 'uiucaidauiucaida'


def load_corefer(input_tab_file):
    offset_entity_corefer = defaultdict(lambda: defaultdict())
    # for lang in input_tab_files:
    for line in open(input_tab_file):
        tabs = line.split('\t')
        offset = tabs[3]  #.replace("asr", "").replace("ocrimg", "").replace("ocrvideo", "")
        corefer_id = tabs[4].split('_')[-1]
        offset_entity_corefer[offset][tabs[5]] = corefer_id
    return offset_entity_corefer


def choose_elmo_model(lang, eng_elmo, ukr_elmo, rus_elmo):
    if lang.startswith('en'):
        return eng_elmo
    elif lang.startswith('uk'):
        return ukr_elmo
    elif lang.startswith('ru'):
        return rus_elmo


def generate_trigger_emb(docid, start_offset, end_offset, ltf_dir, lang,
                         eng_elmo, ukr_elmo, rus_elmo):
    # search_key, sentence, idx
    ltf_file_path = None
    # filetype = None
    # for suffix in ['', 'asr', 'ocrimg', 'ocrvideo']:
    # for ltf_folder in ltf_folders:
    ltf_file_path = os.path.join(ltf_dir, docid + '.ltf.xml')
    if os.path.exists(ltf_file_path):
        # print(ltf_file_path)
        # filetype = ltf_folder.replace('_all', '') + '_' + suffix

        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    sent_tokens = []
                    token_idxs = []
                    seg_beg = int(seg.attrib["start_char"])
                    seg_end = int(seg.attrib["end_char"])
                    if start_offset >= seg_beg and end_offset <= seg_end:
                        for token in seg:
                            if token.tag == "TOKEN":
                                token_text = token.text
                                token_id = int(token.attrib["id"].split('-')[-1])
                                token_beg = int(token.attrib["start_char"])
                                token_end = int(token.attrib["end_char"])
                                if start_offset <= token_beg and end_offset >= token_end:
                                    token_text = '<span style="color:blue">' + token_text + '</span>'
                                    token_idxs.append(token_id)
                                sent_tokens.append(token_text)
                    if len(token_idxs) > 0 and len(token_idxs) <= 5:
                        # trigger_dict[search_key]['sentence'] = sent_tokens
                        # trigger_dict[search_key]['index'] = token_idxs
                        # lang = ltf_folder[:2]
                        model = choose_elmo_model(lang, eng_elmo, ukr_elmo, rus_elmo)
                        # print(len(sent_tokens))
                        sentence_emb = model.sents2elmo([sent_tokens])[0]
                        # print('sentence_emb', sentence_emb)
                        # print(token_idxs)
                        trigger_embs = sentence_emb[token_idxs[0]:(token_idxs[-1]+1)]
                        # print('trigger_embs', trigger_embs)
                        trigger_emb = np.mean(trigger_embs, axis=0)
                        # print('trigger_emb', trigger_emb)
                        return trigger_emb
    if ltf_file_path is None:
        print('[ERROR]NoLTF %s' % docid)
    return None
    # if len(trigger_emb_lists) > 0:
    #     json.dump(trigger_emb_lists, open(os.path.join(output_folder, one_file_id + '.json'), 'w'), indent=4)



def load_entity_vec(ent_vec_files, ent_vec_dir):
    offset_vec = defaultdict(lambda: defaultdict(list))
    # vec_dim = 0

    for ent_vec_file in ent_vec_files:
        ent_vec_type = ent_vec_file.split('/')[-1].replace('.mention.hidden.txt', '').replace('.trigger.hidden.txt', '')
        # print(ent_vec_type)
        for line in open(os.path.join(ent_vec_dir, ent_vec_file)):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 3:
                offset = tabs[1]
                docid = offset.split(':')[0] #.replace('asr', '').replace('ocrimg', '').replace('ocrvideo', '')
                start = int(offset.split(':')[1].split('-')[0])
                end = int(offset.split(':')[1].split('-')[1])
                vec = np.array(tabs[2].split(','), dtype='f')
                # vec_dim = vec.size
                offset_vec[docid][ent_vec_type].append((start, end, vec))
    return offset_vec


def add_filetype(g, one_unique_ke, filetype_str):
    system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/fileType")
    file_type_json_object = {'fileType': filetype_str}
    file_type_json_content = json.dumps(file_type_json_object)
    aifutils.mark_private_data(g, one_unique_ke, file_type_json_content, system)


def load_info(language_id, fine_grained_entity_type_path, freebase_link_mapping, lorelei_link_mapping,
              translation_path):
    fine_grained_entity_dict = json.load(open(fine_grained_entity_type_path))
    freebase_links = json.load(open(freebase_link_mapping))
    lorelei_links = json.load(open(lorelei_link_mapping))

    if 'en' not in language_id:
        translation_dict = json.load(open(translation_path))
    else:
        translation_dict = None

    return lorelei_links, freebase_links, fine_grained_entity_dict, translation_dict


def append_private_data(language_id, input_folder, lorelei_links, freebase_links, fine_grained_entity_dict,
                        translation_dict, offset_vec, offset_entity_corefer, ltf_dir, doc_id_to_root_dict=None,
                        eng_elmo=None, ukr_elmo=None, rus_elmo=None, trigger_vec=None, offset_event_vec=None):

    # count_flag = 0
    for one_file in os.listdir(input_folder):
        # print(one_file)
        if ".ttl" not in one_file:
            continue
        # ent_json_list = dict()
        one_file_id = one_file.replace(".ttl", "")
        if doc_id_to_root_dict is not None:
            root_docid = doc_id_to_root_dict[one_file_id]
        else:
            root_docid = ""
        one_file_path = os.path.join(input_folder, one_file)
        output_file = os.path.join(output_folder, one_file)
        turtle_content = open(one_file_path).read()
        g = Graph().parse(data=turtle_content, format='ttl')

        # # append file type
        # system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/fileType")
        # unique_ke_list = list()
        # for p, s, o in g:
        #     if "http://www.rpi.edu" in o:
        #         if p not in unique_ke_list:
        #             unique_ke_list.append(p)
        # for one_unique_ke in unique_ke_list:
        #     file_type_json_object = {'fileType': language_id}
        #     file_type_json_content = json.dumps(file_type_json_object)
        #     aifutils.mark_private_data(g, one_unique_ke, file_type_json_content, system)

        # append EDL fine_grained_data
        # system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/EDL_FineGrained")
        # for p, s, o in g:
        #     if 'linkTarget' not in s:
        #         continue
        #     linking_info = o.split(':')[-1]
        #     if linking_info in fine_grained_entity_dict:
        #         fine_grained_json_object = fine_grained_entity_dict[linking_info]
        #         fine_grained_json_content = json.dumps(fine_grained_json_object)
        #         aifutils.mark_private_data(g, p, fine_grained_json_content, system)


        # entities = []
        events = []
        args = []
        for s, p, o in g:
            # print(s, p, o)
            if 'type' in p and 'Entity' in o:
                add_filetype(g, s, language_id)
                # entities.append(s)
            elif 'type' in p and 'Event' in o:
                add_filetype(g, s, language_id)
                events.append(s)
            elif 'type' in p and ('Statement' in o or 'Relation' in o):
                add_filetype(g, s, language_id)
                args.append(s)
        # get entities without TITLE/TIME, etc
        entity_type_ttl = defaultdict()
        for entity in g.subjects(predicate=RDF.type, object=AIDA.Entity):
            for assertion in g.subjects(object=entity, predicate=RDF.subject):
                object_assrt = g.value(subject=assertion, predicate=RDF.object)
                predicate_assrt = g.value(subject=assertion, predicate=RDF.predicate)
                # only predicate ==`type`
                if predicate_assrt == RDF.type:
                    entity_type = object_assrt.split('#')[-1]
                    parent_type = entity_type.split('.')[0]
                    if parent_type in ['PER', 'ORG', 'GPE', 'LOC', 'FAC', 'WEA', 'VEH', 'SID', 'CRM', 'BAL']:
                        entity_type_ttl[entity] = entity_type

        entity_offset_map = defaultdict(list)
        event_offset_map = defaultdict(list)
        for s, p, o in g:
            if 'justifiedBy' in p:
                if s in entity_type_ttl: #entities:
                    entity_offset_map[s].append(o)
                if s in events:
                    event_offset_map[s].append(o)


        offset_info = dict()  # offset_info[offset]['startOffset']=start, offset_info[offset]['endOffsetInclusive']=end
        for s, p, o in g:
            p = p.toPython().split('#')[-1]
            if 'startOffset' == p or 'endOffsetInclusive' == p or 'source' == p:
                if s not in offset_info:
                    offset_info[s] = dict()
                offset_info[s][p] = o

        # trigger_emb_lists = defaultdict()
        for event in event_offset_map:
            event_vecs = []
            for one_offset in event_offset_map[event]:
                if len(offset_info[one_offset]) != 3:
                    continue
                for one_offset_type in offset_info[one_offset]:
                    if 'startOffset' in one_offset_type:
                        start_offset = int(offset_info[one_offset][one_offset_type])
                    elif 'endOffsetInclusive' in one_offset_type:
                        end_offset = int(offset_info[one_offset][one_offset_type])
                    elif 'source' in one_offset_type:
                        docid = offset_info[one_offset][one_offset_type].toPython()
                    # search_key = "%s:%d-%d" % (docid, start_offset, end_offset)

                if trigger_vec:
                    # event embedding from files
                    for ent_vec_type in offset_event_vec[docid]:
                        for (vec_start, vec_end, vec) in offset_event_vec[docid][ent_vec_type]:
                            # print(vec_start, vec_end, vec)
                            if vec_start >= start_offset and vec_end <= end_offset:
                                # print(search_key)
                                event_vecs.append(vec)
                else:
                    # event embedding from elmo
                    vec = generate_trigger_emb(docid, start_offset, end_offset,
                                               ltf_dir, language_id,
                                               eng_elmo, ukr_elmo, rus_elmo)
                    if vec is not None:
                        event_vecs.append(vec)

            if len(event_vecs) > 0:
                # print(event_vecs)
                trigger_emb_avg = np.mean(event_vecs, axis=0)
                evt_vec_json_object = {'event_vec': ','.join(['%0.8f' % dim for dim in trigger_emb_avg])}
                evt_vec_json_content = json.dumps(evt_vec_json_object)
                system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/event_representations")
                aifutils.mark_private_data(g, event, evt_vec_json_content, system)
                # trigger_emb_lists[event] = evt_vec_json_content
        # unique_events = []
        # for one_bnode in event_offset_map:
        #     if event_offset_map[one_bnode] in unique_events:
        #         continue
        #     if len(offset_info[one_bnode]) != 2:
        #         continue
        #     for one_offset_type in offset_info[one_bnode]:
        #         if 'startOffset' in one_offset_type:
        #             start_offset = int(offset_info[one_bnode][one_offset_type])
        #         elif 'endOffsetInclusive' in one_offset_type:
        #             end_offset = int(offset_info[one_bnode][one_offset_type])
        #     search_key = "%s:%d-%d" % (one_file_id, start_offset, end_offset)
        #
        #     # append event time
        #     try:
        #         time = time_map[search_key]
        #         time_norm = time_map_norm[search_key]
        #         system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/event_time")
        #         time_json_dict = {'time': time, 'time_norm': time_norm}
        #         time_json_content = json.dumps(time_json_dict)
        #         aifutils.mark_private_data(g, event_offset_map[one_bnode], time_json_content, system)
        #         unique_events.append(event_offset_map[one_bnode])
        #     except KeyError:
        #         pass
        #         # continue

        unique_entities = set()
        # ###### old ########### change to one entity may have multiple offsets
        # for one_bnode in entity_offset_map:
        #     if len(offset_info[one_bnode]) != 2:
        #         continue
        #     for one_offset_type in offset_info[one_bnode]:
        #         if 'startOffset' in one_offset_type:
        #             start_offset = int(offset_info[one_bnode][one_offset_type])
        #         elif 'endOffsetInclusive' in one_offset_type:
        #             end_offset = int(offset_info[one_bnode][one_offset_type])
        #     search_key = "%s:%d-%d" % (one_file_id, start_offset, end_offset)
        for entity in entity_offset_map:
            entity_vecs = []
            entity_type = entity_type_ttl[entity]
            coarse_type = entity_type.split('.')[0]
            for one_offset in entity_offset_map[entity]:
                if len(offset_info[one_offset]) != 3:
                    continue
                for one_offset_type in offset_info[one_offset]:
                    if 'startOffset' in one_offset_type:
                        start_offset = int(offset_info[one_offset][one_offset_type])
                    elif 'endOffsetInclusive' in one_offset_type:
                        end_offset = int(offset_info[one_offset][one_offset_type])
                    elif 'source' in one_offset_type:
                        docid = offset_info[one_offset][one_offset_type].toPython()
                search_key = "%s:%d-%d" % (docid, start_offset, end_offset)


                # append links
                if entity not in unique_entities:
                    # append Freebase linking result
                    try:
                        if search_key in freebase_links:
                            freebase_link = freebase_links[search_key]
                            system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/EDL_Freebase")
                            # freebase_json_dict = {'freebase_link': freebase_link}
                            # freebase_json_content = json.dumps(freebase_json_dict)
                            # aifutils.mark_private_data(g, one_offset, freebase_json_content, system)
                            freebase_json_content = json.dumps({'freebase_link': freebase_link})
                            aifutils.mark_private_data(g, entity, freebase_json_content, system)

                            # append EDL fine_grained_data
                            linking_info = sorted(freebase_link.items(), key=lambda x: x[1]['average_score'], reverse=True)[0][0]
                            # linking_info = freebase_link.split(':')[-1]
                            if linking_info in fine_grained_entity_dict:
                                fine_grained_json_object = fine_grained_entity_dict[linking_info]
                                fine_grained_json_content = json.dumps({'finegrained_type': fine_grained_json_object})
                                system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/EDL_FineGrained")
                                aifutils.mark_private_data(g, entity, fine_grained_json_content, system)

                        # append multiple confidence
                        if search_key in lorelei_links:
                            # lorelei_link_dict = lorelei_links[search_key]
                            # print(lorelei_link_dict)
                            system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/EDL_LORELEI_maxPool")
                            p_link = URIRef('https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/InterchangeOntology#link')
                            p_link_target = URIRef('https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/InterchangeOntology#linkTarget')
                            for lorelei_link_ttl in g.objects(subject=entity, predicate=p_link):
                                link_target = str(g.value(subject=lorelei_link_ttl, predicate=p_link_target))#.split(':')[-1]
                                # print('link_target', link_target)
                                if search_key not in lorelei_links or link_target not in lorelei_links[search_key]: #???
                                    confidence = 0.001
                                else:
                                    confidence = lorelei_links[search_key][link_target]
                                # print('confidence', confidence)
                                aifutils.mark_confidence(g, lorelei_link_ttl, confidence, system)

                        # append corefer info
                        if search_key in offset_entity_corefer:
                            # print(one_file_id, search_key, entity_ttl, offset_entity_corefer[search_key])
                            if coarse_type in offset_entity_corefer[search_key]:
                                corefer_id = offset_entity_corefer[search_key][coarse_type]
                                # print(search_key, id)
                                system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/coreference")
                                # cipher = AES.new(secret_key, AES.MODE_ECB)  # never use ECB in strong systems obviously
                                corefer_id_encoded = base64.b64encode(('%s%s' % (root_docid, corefer_id)).encode('utf-8')).decode("utf-8")
                                corefer_json_dict = {'coreference': corefer_id_encoded} #str(uuid.UUID(corefer_id).hex)}
                                corefer_json_content = json.dumps(corefer_json_dict)
                                aifutils.mark_private_data(g, entity, corefer_json_content, system)

                        # save entity
                        unique_entities.add(entity)
                    except KeyError as e:
                        traceback.print_exc()
                        pass


                # append translation (mention-level)
                if 'en' in language_id:
                    continue
                try:
                    translation_list = translation_dict[search_key]
                    system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/EDL_Translation")
                    translation_json_dict = {'translation': translation_list}
                    translation_json_content = json.dumps(translation_json_dict)
                    aifutils.mark_private_data(g, one_offset, translation_json_content, system)
                except KeyError:
                    pass
                    # continue


                # collect entity vectors (mention-level)
                for ent_vec_type in offset_vec[docid]:
                    for (vec_start, vec_end, vec) in offset_vec[docid][ent_vec_type]:
                        # print(vec_start, vec_end, vec)
                        if vec_start >= start_offset and vec_end <= end_offset:
                            # print(search_key)
                            entity_vecs.append(vec)
            # append entity vectors (mention-level)
            if len(entity_vecs) > 0:
                entity_vec = np.average(entity_vecs, 0)
                # print(entity, entity_vec)
                system = aifutils.make_system_with_uri(g, "http://www.rpi.edu/entity_representations")
                ent_vec_json_object = {'entity_vec_space': ent_vec_type,
                                       'entity_vec': ','.join(['%0.8f' % dim for dim in entity_vec])}
                ent_vec_json_content = json.dumps(ent_vec_json_object)
                # print(ent_vec_json_content)
                aifutils.mark_private_data(g, entity, ent_vec_json_content, system)
                # ent_json_list[entity] = ent_vec_json_content
                break


        g.serialize(destination=output_file, format='turtle')


    print("Now we have append the private data for %s" % language_id)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--language_id', type=str,
                        help='Options: en | en_asr | en_ocr')
    # parser.add_argument('--data_source', type=str, default='',
    #                     help='Options: | _asr | _ocr | _ocr_video')
    parser.add_argument('--initial_folder', type=str,
                        help='input directory (initial)')
    parser.add_argument('--output_folder', type=str,
                        help='output directory after adding private data (initial_private_data)')
    parser.add_argument('--fine_grained_entity_type_path', type=str,
                        help='%s.linking.freebase.fine.json')
    parser.add_argument('--freebase_link_mapping', type=str,
                        help='edl/freebase_private_data.json')
    parser.add_argument('--lorelei_link_mapping', type=str,
                        help='edl/lorelei_private_data.json')
    parser.add_argument('--translation_path', type=str, default='',
                        help='%s.linking.freebase.translations.json')
    parser.add_argument('--event_embedding_from_file', action='store_true',
                        help='append event embedding from OneIE')
    parser.add_argument('--ent_vec_dir', type=str, default='',
                        help='ent_vec_dir')
    parser.add_argument('--ent_vec_files', nargs='+', type=str,
                        help='ent_vec_files')
    parser.add_argument('--evt_vec_dir', type=str, default='',
                        help='evt_vec_dir')
    parser.add_argument('--evt_vec_files', nargs='+', type=str,
                        help='evt_vec_files')
    parser.add_argument('--ltf_dir', type=str, default='',
                        help='ltf_dir')
    parser.add_argument('--edl_tab', type=str, default='',
                        help='edl_tab')
    parser.add_argument('--parent_child_tab_path', type=str, default='',
                        help='parent_child_tab_path')
    parser.add_argument('--child_column_idx', type=int, default=2,
                        help='the column_id of uid in parent_children.tab. Column_id starts from 0. ')
    parser.add_argument('--parent_column_idx', type=int, default=7,
                        help='the column_id of parent_uid in parent_children.tab. Column_id starts from 0. ')

    args = parser.parse_args()

    initial_folder = args.initial_folder
    output_folder = args.output_folder
    fine_grained_entity_type_path = args.fine_grained_entity_type_path
    freebase_link_mapping = args.freebase_link_mapping
    lorelei_link_mapping = args.lorelei_link_mapping
    translation_path = args.translation_path
    ent_vec_dir = args.ent_vec_dir
    ent_vec_files = args.ent_vec_files
    evt_vec_dir = args.evt_vec_dir
    evt_vec_files = args.evt_vec_files
    event_embedding_from_file=args.event_embedding_from_file
    ltf_dir = args.ltf_dir
    edl_tab = args.edl_tab
    parent_child_tab_path = args.parent_child_tab_path
    child_column_idx = args.child_column_idx
    parent_column_idx = args.parent_column_idx

    # lang = args.lang
    # data_source = args.data_source
    # language_id = '%s%s' % (lang, data_source)

    # language_id = sys.argv[1]
    language_id = args.language_id
    lang = language_id.split('_')[0]

    # result_path = "/data/m1/lim22/aida2019/dryrun_3/0610/%s" % language_id
    #
    # # Change the input folder
    # initial_folder = os.path.join(result_path, "initial")
    # # Change the output folder
    # output_folder = os.path.join(result_path, "initial_private_data")

    # # Change the fine-grained folder
    # fine_grained_path = "/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0610%s/" % (lang, language_id.replace(lang, ""))
    #
    # # English has no translation
    # translation_path = os.path.join(fine_grained_path, "%s.linking.freebase.translations.json" % lang)
    # # translation_path = "/nas/data/m1/panx2/tmp/aida/eval/2019/ru/0327_asr/ru.linking.freebase.translations.json"
    #
    # fine_grained_entity_type_path = os.path.join(fine_grained_path, "%s.linking.freebase.fine.json" % lang)
    # # freebase_links_mapping = os.path.join(fine_grained_path, "%s.linking.freebase.tab" % lang)
    # freebase_link_mapping = os.path.join(result_path, "edl/freebase_private_data.json")
    #
    # lorelei_link_mapping = os.path.join(result_path, 'edl/lorelei_private_data.json')
    #
    # # time_dict = os.path.join(result_path, "event/time_mapping.txt")

    if os.path.exists(output_folder) is False:
        os.mkdir(output_folder)

    lorelei_links, freebase_links, fine_grained_entity_dict, translation_dict = load_info(
        language_id, fine_grained_entity_type_path, freebase_link_mapping,
        lorelei_link_mapping, translation_path)

    offset_vec = load_entity_vec(ent_vec_files, ent_vec_dir)
    offset_entity_corefer = load_corefer(edl_tab)
    if os.path.exists(parent_child_tab_path):
        doc_id_to_root_dict = load_doc_root_mapping(parent_child_tab_path, child_column_idx, parent_column_idx)
    else:
        doc_id_to_root_dict = None

    if args.event_embedding_from_file:
        eng_elmo = None
        ukr_elmo = None
        rus_elmo = None
        offset_event_vec = load_entity_vec(evt_vec_files, evt_vec_dir)
    else:
        eng_elmo = Embedder('/postprocessing/ELMoForManyLangs/eng.model')
        ukr_elmo = Embedder('/postprocessing/ELMoForManyLangs/ukr.model')
        rus_elmo = Embedder('/postprocessing/ELMoForManyLangs/rus.model')
        offset_event_vec = None

    append_private_data(language_id, initial_folder, lorelei_links, freebase_links,
                        fine_grained_entity_dict, translation_dict, offset_vec, offset_entity_corefer,
                        ltf_dir, doc_id_to_root_dict,
                        eng_elmo=eng_elmo, ukr_elmo=ukr_elmo, rus_elmo=rus_elmo,
                        trigger_vec=args.event_embedding_from_file, offset_event_vec=offset_event_vec)

