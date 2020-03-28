import requests
import os
import json
import argparse
import io

parser = argparse.ArgumentParser(description='Call the aida event API acquire output')
parser.add_argument('-e', '--input_path', help='Event CS list path', required=True)
parser.add_argument('-c', '--certainty', help='hedge folder', required=True)
parser.add_argument('-o', '--output_path', help='Output CS file path', required=True)
args = vars(parser.parse_args())

event_input_path = args['input_path']
hedge_input_path = args['certainty']
event_output_path = args['output_path']

temp_dict = dict()

temp_dict['event_before_assert'] = open(event_input_path, encoding='utf-8').read()

temp_dict['event_certainty'] = dict()
for one_certainty_file in os.listdir(hedge_input_path):
    one_certainty_file_path = os.path.join(hedge_input_path, one_certainty_file)
    temp_dict['event_certainty'][one_certainty_file] = list()
    for one_line in open(one_certainty_file_path, encoding='utf-8'):
        one_dict = json.loads(one_line)
        temp_dict['event_certainty'][one_certainty_file].append(one_dict)

json_string = json.dumps(temp_dict)
r = requests.post('http://127.0.0.1:5234/aida_event_add_hedge', json=json_string)
if r.status_code == 200:
    print("Successfully added hedge information")
    f = io.open(event_output_path, 'w')
    f.write(r.text)
    f.close()
else:
    print(r.status_code)
