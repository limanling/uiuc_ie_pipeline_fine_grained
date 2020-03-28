import requests
import os
import json
import argparse
import codecs

# input_event_cs_file_path = 'uk_events_eval.cs'
# output_event_coreference_output_file_path = 'test_test.cs'

parser = argparse.ArgumentParser(description='Call the aida event coreference API acquire output')
parser.add_argument('-i', '--event_cs', help='Event CS file path', required=True)
parser.add_argument('-o', '--output_path', help='Event Corference CS output file path', required=True)
parser.add_argument('-r', '--rsd_dir', help='path to dir of rsd files')
parser.add_argument('-x', '--xdoc', default = False, action='store_true', help='switch for cross document coreference')
parser.add_argument('-n', '--doc_per_doc', default = 100 ,help='number of documents for each topic')
args = vars(parser.parse_args())

input_event_cs_file_path = args['event_cs']
output_event_coreference_output_file_path = args['output_path']

temp_dict = dict()
with codecs.open(input_event_cs_file_path, 'r', 'utf-8') as f:
	temp_dict['event_cs'] = f.readlines()

temp_dict['xdoc'] = args['xdoc']
temp_dict['rsd_dir'] = args['rsd_dir']
temp_dict['doc_per_doc'] = args['doc_per_doc']
rsd_data = []
rsd_doc_index = {}
if args['xdoc']:
        ii = 0
        for doc in os.listdir(args['rsd_dir']):
                rsd_doc_index[str(ii)] = doc
                ii += 1
                with open(os.path.join(args['rsd_dir'], doc)) as f:
                        article = f.read()
                        rsd_data.append(article)
temp_dict['rsd_data'] = rsd_data
temp_dict['rsd_doc_index'] = rsd_doc_index

json_string = json.dumps(temp_dict)
r = requests.post('http://127.0.0.1:6001/aida_event_coreference_eng', json=json_string)
if r.status_code == 200:
    print("Successfully extracted events")
    f = codecs.open(output_event_coreference_output_file_path, 'w', 'utf-8')
    f.write(r.text)
    f.close()
else:
    print(r.status_code)
