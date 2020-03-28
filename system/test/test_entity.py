import requests
import traceback
import json
import os
import sys

lang = sys.argv[1]
# print('lang', lang)
test_dir = sys.argv[2]
output_dir = os.path.join(test_dir, 'output', 'entity')
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

ltf_dir = os.path.join(test_dir, 'ltf')
rsd_dir = os.path.join(test_dir, 'rsd')

for en_ltf_file in os.listdir(ltf_dir):
    doc_id = en_ltf_file.replace('.ltf.xml', '')
    # print(doc_id)
    en_ltf_str = open(os.path.join(ltf_dir, doc_id+'.ltf.xml'), 'r').read()
    en_rsd_str = open(os.path.join(rsd_dir, doc_id+'.rsd.txt'), 'r').read()

    ans = requests.post(
        'http://0.0.0.0:5500/tagging',
        data={
            'ltf': en_ltf_str,
            'rsd': en_rsd_str,
            'doc_id': doc_id,
            'lang': lang
        }
    )

    # print(ans.status_code)
    # print('ans.text', ans.text)

    ans = json.loads(ans.text)
    with open(os.path.join(output_dir, 'all.bio'), 'a') as writer:
        writer.write(ans['bio'])
    with open(os.path.join(output_dir, 'all.tab'), 'a') as writer:
        writer.write(ans['tab'])
    with open(os.path.join(output_dir, 'all.tsv'), 'a') as writer:
        writer.write(ans['tsv'])
    # print('bio')
    # print(ans['bio'])
    # print('tab')
    # print(ans['tab'])
    # print('tsv')
    # print(ans['tsv'])




