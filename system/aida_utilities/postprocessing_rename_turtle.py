import os
import shutil
from rdflib import Graph
import sys
import argparse
from parent_child_util import get_column_idx

parser = argparse.ArgumentParser()
parser.add_argument('parent_child_mapping_file', type=str,
                    help='the parent_child mapping file path')
parser.add_argument('parent_child_mapping_file_sorted', type=int,
                    help='1 if the parent_child mapping file is sorted.tab, otherwise 0')
# parser.add_argument('raw_id_column', type=int,
#                     help='the child column in parent_child_tab_path')
# parser.add_argument('rename_id_column', type=int,
#                     help='the parent column in parent_child_tab_path')
parser.add_argument('input_folder', type=str,
                    help='the input directory where the files use child_file_id')
parser.add_argument('output_folder', type=str,
                    help='the output directory where the files use parent_file_id')

args = parser.parse_args()
parent_child_tab_path = args.parent_child_mapping_file
# raw_id_column = args.raw_id_column
# rename_id_column = args.rename_id_column
input_folder = args.input_folder
output_folder = args.output_folder

raw_id_column, rename_id_column, date_column = get_column_idx(sorted=args.parent_child_mapping_file_sorted!=0)

if os.path.exists(output_folder) is False:
    os.mkdir(output_folder)
else:
    shutil.rmtree(output_folder)
    os.mkdir(output_folder)

doc_id_to_root_dict = dict()

f = open(parent_child_tab_path)
f.readline()

for one_line in f:
    one_line = one_line.strip()
    one_line_list = one_line.split('\t')
    doc_id = one_line_list[raw_id_column] # child_uid
    root_id = one_line_list[rename_id_column] # parent_uid
    doc_id_to_root_dict[doc_id] = root_id

for one_file in os.listdir(input_folder):
    if '.ttl' not in one_file and '.turtle' not in one_file:
        continue
    # print(one_file)
    file_id = one_file.replace('.ttl', '').replace('.turtle', '')
    root_id = doc_id_to_root_dict[file_id]
    src_path = os.path.join(input_folder, one_file)
    dst_path = os.path.join(output_folder, '%s.ttl' % root_id)
    if os.path.exists(dst_path) is False:
        shutil.copy(src_path, dst_path)
    else:
        # print('Repeated!')
        # print(one_file)
        # print(dst_path)
        turtle_content = open(dst_path).read()
        g = Graph().parse(data=turtle_content, format='ttl')
        source_turtle_content = open(src_path).read()
        g.parse(data=source_turtle_content, format='ttl')
        g.serialize(g.serialize(destination=dst_path, format='ttl'))

print("Now we have changed the turtle file names for %s" % input_folder)