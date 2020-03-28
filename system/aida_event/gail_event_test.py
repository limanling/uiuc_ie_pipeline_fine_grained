import requests
import os
import json
import argparse
import io

# input_file_list_file_path = 'data/rico_hurricane/ltf_lst'
# input_ltf_folder_path = 'data/rico_hurricane/ltf'
# input_edl_cs_file_path = 'data/rico_hurricane/edl/merged.cs'
# input_edl_tab_file_path = 'data/rico_hurricane/edl/merged.tab'
# input_filler_cs_file_path = 'data/rico_hurricane/edl/filler_en.cs'
# output_event_output_file_path = 'data/rico_hurricane/event/en.evt.cs'

parser = argparse.ArgumentParser(description='Call the aida event API acquire output')
parser.add_argument('-l', '--list', help='LTF file list path', required=True)
parser.add_argument('-f', '--ltf_folder', help='LTF folder path', required=True)
parser.add_argument('-e', '--edl_cs', help='EDL CS file path', required=True)
parser.add_argument('-t', '--edl_tab', help='EDL tab file path', required=True)
parser.add_argument('-i', '--filler_cs', help='Filler CS file path', required=True)
parser.add_argument('-o', '--output_path', help='Output CS file path', required=True)
args = vars(parser.parse_args())

input_file_list_file_path = args['list']
input_ltf_folder_path = args['ltf_folder']
input_edl_cs_file_path = args['edl_cs']
input_edl_tab_file_path = args['edl_tab']
input_filler_cs_file_path = args['filler_cs']
output_event_output_file_path = args['output_path']

if not os.path.exists(os.path.dirname(output_event_output_file_path)):
    os.makedirs(os.path.dirname(output_event_output_file_path), exist_ok=True)


temp_dict = dict()
temp_dict['edl_cs'] = io.open(input_edl_cs_file_path, encoding='utf-8').read()
temp_dict['edl_tab'] = io.open(input_edl_tab_file_path, encoding='utf-8').read()
temp_dict['filler_cs'] = io.open(input_filler_cs_file_path, encoding='utf-8').read()
temp_dict['input'] = dict()
for one_line in io.open(input_file_list_file_path):
    one_line = one_line.strip()
    one_ltf_xml_file_path = os.path.join(input_ltf_folder_path, one_line)
    ltf_content = io.open(one_ltf_xml_file_path).read()
    if '<TEXT/>' in ltf_content:
        # No text content
        continue
    temp_dict['input'][one_line] = dict()
    temp_dict['input'][one_line]['ltf'] = ltf_content

json_string = json.dumps(temp_dict)
r = requests.post('http://127.0.0.1:5234/aida_event_en_imitation', json=json_string)
if r.status_code == 200:
    print("Successfully extracted events")
    f = io.open(output_event_output_file_path, 'w')
    f.write(r.text)
    f.close()
else:
    print(r.status_code)
