import os
import sys
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))

import argparse
from collections import defaultdict
from aida_utilities.ltf_util import parse_offset_str

parser = argparse.ArgumentParser()
# parser.add_argument('language_id', type=str, help='lang.')
# parser.add_argument('chunking_path', type=str, help='chunking_path')
parser.add_argument('chunking_file', type=str, help='chunking_file')
parser.add_argument('input_cs', type=str, help='input cold start')
parser.add_argument('output_cs', default=str, help='output_cs')
args = parser.parse_args()

# language_id = args.language_id
# chunking_path = args.chunking_path
chunking_file = args.chunking_file
input_cs = args.input_cs
output_cs = args.output_cs

chunks = defaultdict(list)
# for chunking_file_name in os.listdir(chunking_path):
# chunking_file = os.path.join(chunking_path, chunking_file_name)
for line in open(chunking_file):
    line = line.rstrip('\n')
    tabs = line.split('\t')
    if len(tabs) < 2:
        continue
    docid = tabs[0]
    chunk_start = int(tabs[1])
    chunk_end = int(tabs[2])
    str = tabs[3]
    chunks[docid].append((chunk_start, chunk_end, str))  # sorted
# print('chunk dict size : ', len(chunks))

# get the nominal singletons
## get the entities with name mentions
# name_entities = set()
# for line in open(input_cs):
#     line = line.rstrip('\n')
#     if line.startswith(':Entity'):
#         tabs = line.split('\t')
#         if 'mention' == tabs[1]:
#             name_entities.add(tabs[0])

nominal_info_extent_map = dict()
nominal_info_offset_map = dict()
entity_type = dict()
for line in open(input_cs):
    line = line.rstrip('\n')
    if line.startswith(':Entity'):
        tabs = line.split('\t')
        entity_id = tabs[0]
        if 'nominal_mention' == tabs[1]:
            # if entity_id not in name_entities:
                # print(entity_id)
            offset = tabs[3]
            nomimal_docid, nomimal_start, nomimal_end = parse_offset_str(offset)
            for (chunk_start, chunk_end, extent) in chunks[nomimal_docid]:
                if nomimal_start >= chunk_start and nomimal_end <= chunk_end:
                    # nominal_info_map[offset]['extent'] = extent
                    # nominal_info_map[offset]['offset'] = '%s:%d-%d' % (nomimal_docid, start, end)
                    if chunk_start == nomimal_start and nomimal_end == chunk_end:
                        continue
                    nominal_info_extent_map[offset] = extent
                    nominal_info_offset_map[offset] = '%s:%d-%d' % (nomimal_docid, chunk_start, chunk_end)
                    # print('NOM    : ', tabs[2][1:-1], ' -> ', extent)
        elif 'type' == tabs[1]:
            entity_type[entity_id] = tabs[2].split('#')[-1]


# nominal_info_extent_map = dict()
# nominal_info_offset_map = dict()
# for line in open(input_cs):
#     line = line.rstrip('\n')
#     if line.startswith(':Entity'):
#         tabs = line.split('\t')
#         entity_id = tabs[0]
#         if 'canonical_mention' == tabs[1]:
#             offset = tabs[3]
#             nomimal_docid, nomimal_start, nomimal_end = parse_offset_str(offset)
#             for (start, end, extent) in chunks[nomimal_docid]:
#                 if nomimal_start >= start and nomimal_end <= end:
#                     if nomimal_start == start and nomimal_end == end:
#                         continue
#                     nominal_info_extent_map[offset] = extent
#                     nominal_info_offset_map[offset] = '%s:%d-%d' % (nomimal_docid, start, end)
#                     if entity_id in name_entities:
#                         print('NAM    : ', tabs[2][1:-1], ' -> ', extent)
#                     else:
#                         print('NOM/PRO: ', tabs[2][1:-1], ' -> ', extent)
#                 elif nomimal_start > end:
#                     # sorted by index
#                     break

del chunks

writer = open(output_cs, 'w')
writer_log = open(output_cs.replace('.cs', '.log'), 'w')
for line in open(input_cs):
    line = line.rstrip('\n')
    if line.startswith(':Entity'):
        tabs = line.split('\t')
        if not entity_type[tabs[0]].startswith('VAL') and not entity_type[tabs[0]].startswith('TTL'):
            if 'canonical_mention' == tabs[1]:
                offset = tabs[3]
                if offset in nominal_info_extent_map:
                    writer_log.write('%s\t%s\t%s\n' % (entity_type[tabs[0]], offset, nominal_info_offset_map[offset]))
                    writer.write('%s\t%s\t"%s"\t%s\t%s\n' % (tabs[0], tabs[1], nominal_info_extent_map[offset],
                                                             nominal_info_offset_map[offset], tabs[4]))
                    continue
                # else:
                #     print('No extent for nominal canonical_mention')
            # elif 'nominal_mention' == tabs[1]:
            #     offset = tabs[3]
            #     if offset in nominal_info_extent_map:
            #         writer.write('%s\t%s\t"%s"\t%s\t%s\n' % (tabs[0], tabs[1], nominal_info_extent_map[offset],
            #                                                  nominal_info_offset_map[offset], tabs[4]))
            #         continue
    writer.write('%s\n' % line)
writer.flush()
writer.close()
writer_log.flush()
writer_log.close()
