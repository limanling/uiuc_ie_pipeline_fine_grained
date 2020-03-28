import sys
import os

test_dir = sys.argv[1]

ltf_dir = os.path.join(test_dir, 'ltf')
rsd_dir = os.path.join(test_dir, 'rsd')

for ltf_file in os.listdir(ltf_dir):
    doc_id = ltf_file.replace('.ltf.xml', '')
    print(doc_id)