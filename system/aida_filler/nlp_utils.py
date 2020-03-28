import requests
import os
import argparse
import io
import time

annotators = 'tokenize, ssplit, pos, lemma, ner, regexner, depparse, entitymentions'
def preprocess(rsd_file_list, core_nlp_output_paths):
    if not os.path.exists(core_nlp_output_paths):
        os.makedirs(core_nlp_output_paths)
    rsd_files = io.open(rsd_file_list, encoding='utf-8').read().splitlines()
    for rsd_file in rsd_files:
        file = io.open(rsd_file, encoding='utf-8')
        input_string = file.read()
        # r = requests.post('http://localhost:9000/?properties={"annotators":"%s","outputFormat":"json"}' % (annotators),
        r = requests.post('http://localhost:9000',
                          data=input_string.encode('utf-8'))
        if r.status_code == 200:
            t_path = os.path.join(core_nlp_output_paths, os.path.split(rsd_file)[1]+".json")
            with io.open(t_path, 'w', encoding="utf-8") as outfile:
                outfile.write(r.text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filler Extraction')
    parser.add_argument('--rsd_list', type=str, help='list of rsd files')
    parser.add_argument('--corenlp_dir', type=str, help='path of the directory of CoreNLP outputs')
    args = parser.parse_args()

    st = time.time()
    preprocess(args.rsd_list, args.corenlp_dir)
    print('Running Time: %d' % (time.time()-st))