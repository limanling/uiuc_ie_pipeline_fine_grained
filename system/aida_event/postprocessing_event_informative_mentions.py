#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 17:46:35 2019

@author: samyaza
"""

import os
import argparse
import xml.etree.ElementTree as ET
import codecs

parser = argparse.ArgumentParser()
parser.add_argument('ltf_dir', type=str, help='ltf_dir')
parser.add_argument('input_cs_file', type=str, help='input cold start')
parser.add_argument('output_cs_file', type=str, help='output cold start')
args = parser.parse_args()

cs_file_path = args.input_cs_file
informative_file_path = args.output_cs_file
ltf_path = args.ltf_dir
# cs_file_path = '/nas/data/m1/lim22/aida2019/dryrun_3/0610/en_ocr_img/event/events_tme.cs'
# informative_file_path = '/nas/data/m1/subbua/aida_dryruns/dryrun0610/en_ocr_img_informative.cs'
# ltf_path = '/data/m1/lim22/aida2019/dryrun_3/source/en_ocr_img/'

ltf_sent_dict = dict()
ltffiles = os.listdir(ltf_path)
newlines = []
start = ''
end = ''

for fil in ltffiles:
    
        # if '._' in fil:
        #     continue

        if not fil.endswith('.ltf.xml'):
            continue

        ltffile = fil.strip().split('.')[0]
        ltf_sent_dict[ltffile] = dict()
        ltffilepath = os.path.join(ltf_path, ltffile + '.ltf.xml')
        
        with codecs.open(ltffilepath, 'r', encoding='utf-8') as mafile:
            ma = mafile.read()
            root = ET.fromstring(ma)
            
            for seg in root[0][0]:
                original_start = seg.get('start_char')
                original_end = seg.get('end_char')
                child = seg.find('ORIGINAL_TEXT')
                ltf_sent_dict[ltffile][original_start] = [original_end, child.text]


with open(cs_file_path, 'r', encoding='utf-8') as cs_doc:
    cs = cs_doc.read().strip()
    for line in cs.split('\n'):
        ele = line.split('\t')
        if len(ele)<3:
            newlines.append(line)
            continue
        if ':Event' not in ele[0]:
            newlines.append(line)
            continue
        if 'canonical_mention' in ele[1]:
            filename, offsets = ele[3].split(':')
            start, end = offsets.split('-')
            for ltfsent in ltf_sent_dict[filename]:
                if int(start) in range(int(ltfsent), int(ltf_sent_dict[filename][ltfsent][0])):
                    canonical = ltf_sent_dict[filename][ltfsent][1]
                    canonical_ment = filename+':'+ltfsent+'-'+ltf_sent_dict[filename][ltfsent][0]
                    break
            newlines.append(ele[0] + '\t' + ele[1] + '\t"' + canonical + '"\t' + canonical_ment + '\t' + ele[4])
        elif ':Entity' in ele[2]:
            argfilename, argoffsets = ele[3].split(':')
            argstart, argend = argoffsets.split('-')
            if int(start) < int(argstart):
                argstart = start
            if int(end) > int(argend):
                argend = end
            if int(argend) < int(argstart):
                print(canonical_ment, argstart, argend, filename)
            if filename != argfilename:
                print('check this')
            newlines.append(ele[0]+ '\t' + ele[1] + '\t' + ele[2] + '\t' + filename+':'+argstart+'-'+argend + '\t' + ele[4])
        else:
            newlines.append(line)


with open(informative_file_path, 'w', encoding = 'utf-8') as o:
    o.write('\n'.join(newlines))