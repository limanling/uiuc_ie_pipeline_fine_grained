import os
from collections import defaultdict
import shutil

full_cs = '/nas/data/m1/lim22/aida2019/i1/en_ta1/en_full_link_conf.cs'
output_cs_separate_path = '/nas/data/m1/lim22/aida2019/i1/en_ta1/cs/'
if os.path.exists(output_cs_separate_path):
    shutil.rmtree(output_cs_separate_path)
os.makedirs(output_cs_separate_path)


# doc_info=defaultdict(list)
kb_doc_mapping = defaultdict(set)
lines = open(full_cs).readlines()
for line in lines:
    line = line.rstrip('\n')
    tabs = line.split('\t')
    if len(tabs) > 1:
        if tabs[1] != 'type' and tabs[1] != 'link':
            kb_id = tabs[0]
            offset = tabs[3]
            doc = offset[:offset.find(':')]
            # doc_info[doc].append(kb_id)
            kb_doc_mapping[kb_id].add(doc)

doc_lines=defaultdict(list)
for line in lines:
    line = line.rstrip('\n')
    tabs = line.split('\t')
    if len(tabs) > 1:
        if tabs[1] == 'type' or tabs[1] == 'link':
            for doc in kb_doc_mapping[tabs[0]]:
                doc_lines[doc].append(line)
        else:
            offset = tabs[3]
            doc_str = offset[:offset.find(':')]
            doc_lines[doc_str].append(line)

for doc in doc_lines:
    writer = open(os.path.join(output_cs_separate_path, '%s.cs' % doc), 'w')
    writer.write('RPI_BLENDER\n\n')
    for line in doc_lines[doc]:
        writer.write('%s\n' % line)
    writer.flush()
    writer.close()
