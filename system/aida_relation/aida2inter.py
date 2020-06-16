import argparse
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ET
import os
from xml.etree.ElementTree import fromstring
import time


def mkdir(output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    else:
        print("%s is existed" % output_dir)


def assembly_list(l_list):
    new_list = []
    for i in range(len(l_list) - 1):
        for j in range(len(l_list) - i - 1):
            new_list.append([l_list[i], l_list[i + j + 1]])
    return new_list


#########################################################
# doc2mention --- HC000T6IX: [[1, 7], [38, 47], ....,]
# mention2type --- 'HC00007XV:187-192': 'GPE'
#########################################################
def doc_to_men_to_type(edl_tab_string):
    mention2type = {}
    doc2mention = {}
    for line in edl_tab_string.split("\n"):
        temp = line.strip().split("\t")
        doc_id, mention_offset = temp[3].strip().split(":")
        entity_type = temp[5].strip()
        mention_id = temp[3].strip()
        if mention_id not in mention2type:
            mention2type[mention_id] = entity_type
        if doc_id not in doc2mention:
            doc2mention[doc_id] = [mention_offset.split("-")]
        else:
            doc2mention[doc_id].append(mention_offset.split("-"))
    return doc2mention, mention2type


##############################################################################
# doc2segment --- {'HC00007XV': {'segment-0': [1, 48], 'segment-1': [52, 104]}}

# docseg2mention --- {'HC00002Y5': {'segment-0': [['1', '4'],['5','7']], 'segment-1': [['62', '68']}

# doc2segtext --- {'HC00002Y5': {'segment-0': ['MH17'], 'segment-1': ['While',
# 'western']}}

# doc2segoffset --- {'HC00002Y5': {'segment-0': [['1', '4'], ['5', '5'], ['7', '13']]}}
###############################################################################
def doc_to_segment(doc2men_dict, ltf_json_dic):
    doc2segment = {}
    docseg2mention = {}
    doc2segtext = {}
    doc2segoffset = {}
    for key in doc2men_dict:
        domobj = xmldom.parseString(ltf_json_dic[key])
        elementobj = domobj.documentElement
        subElementObj = elementobj.getElementsByTagName("SEG")
        temp = {}
        for i in range(len(subElementObj)):
            temp[subElementObj[i].getAttribute("id")] = \
                [int(subElementObj[i].getAttribute("start_char")), int(subElementObj[i].getAttribute("end_char"))]
        doc2segment[key] = temp
        # doc2seg2mention
        temp_seg2mention_dict = {}
        for mention in doc2men_dict[key]:
            for seg in doc2segment[key]:
                if doc2segment[key][seg][0] <= int(mention[1]) <= doc2segment[key][seg][1]:
                    if seg not in temp_seg2mention_dict:
                        temp_seg2mention_dict[seg] = [mention]
                    else:
                        temp_seg2mention_dict[seg].append(mention)
        docseg2mention[key] = temp_seg2mention_dict
        # seg_to_text, seg_to_offset
        root = ET.fromstring(ltf_json_dic[key])
        # root = tree.getroot()
        temp_seg_text = {}
        temp_seg_offset = {}
        for doc in root:
            for text in doc:
                for seg in text:
                    if seg.attrib["id"] not in temp_seg_text:
                        temp_seg_text[seg.attrib["id"]] = []
                        temp_seg_offset[seg.attrib["id"]] = []
                    for token in seg:
                        if token.tag == "TOKEN":
                            temp_seg_text[seg.attrib["id"]].append(token.text)
                            temp_seg_offset[seg.attrib["id"]].append([token.attrib["start_char"],
                                                                      token.attrib["end_char"]])
        doc2segtext[key] = temp_seg_text
        doc2segoffset[key] = temp_seg_offset
    return doc2segment, docseg2mention, doc2segtext, doc2segoffset


def doc_to_offset(f_list, raw_data_path, raw_data_path1=None):
    temp_doc_offset = {}
    for item in f_list:
        fpath = os.path.join(raw_data_path, item + ".ltf.xml")
        if not os.path.exists(fpath):
            fpath = os.path.join(raw_data_path1, item + ".ltf.xml")
        tree = ET.parse(fpath)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    for token in seg:
                        if token.tag == "TOKEN":
                            if item not in temp_doc_offset:
                                temp_doc_offset[item] = [token.attrib["end_char"]]
                            else:
                                temp_doc_offset[item].append(token.attrib["end_char"])
    return temp_doc_offset


