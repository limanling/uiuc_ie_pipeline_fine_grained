import sys
import os
import requests
# import subprocess
# from nominal_corefer_en import get_nominal_corefer
import json
import codecs


def typing(lang, cfet_json_file, fine_grain_model):

    url = 'http://0.0.0.0:5500/typing'

    try:
        json_str = codecs.open(cfet_json_file, encoding="utf-8").read()
        input_data = {
            'json': json_str,
            'lang': lang
        }
        r = requests.post(url, data=input_data)
        if r.status_code != 200:
            return
        ans = json.loads(r.text)
        with codecs.open(fine_grain_model, 'a', encoding="utf-8") as fw:
            fw.write(ans['tsv'])
            fw.write('\n')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = 'unexpected error: %s | %s | %s' % \
              (exc_type, exc_obj, exc_tb.tb_lineno)
        print(msg)


def typingbio(lang, bio_file, fine_grain_model):

    url = 'http://0.0.0.0:5500/typingbio'

    try:
        bio_str = codecs.open(bio_file, encoding="utf-8").read()
        input_data = {
            'bio': bio_str,
            'lang': lang
        }
        r = requests.post(url, data=input_data)
        if r.status_code != 200:
            return
        ans = json.loads(r.text)
        with codecs.open(fine_grain_model, 'a', encoding="utf-8") as fw:
            fw.write(ans['tsv'])
            fw.write('\n')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = 'unexpected error: %s | %s | %s' % \
              (exc_type, exc_obj, exc_tb.tb_lineno)
        print(msg)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(sys.argv)
        print('USAGE: python <lang> <cfet_json_file> <fine_grain_model output file>')
        exit()
    lang = sys.argv[1]
    # cfet_json_file = sys.argv[2]
    bio_file = sys.argv[2]
    fine_grain_model = sys.argv[3]

    # typing(lang, cfet_json_file, fine_grain_model)
    typingbio(lang, bio_file, fine_grain_model)
