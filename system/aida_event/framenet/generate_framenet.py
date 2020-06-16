import os
import sys
# import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ET
import argparse

def doc_to_segment(ltf_path, ltf_file, to_path):
    f = open(os.path.join(to_path, ltf_file.replace('.xml', '.txt')), 'w')

    tree = ET.parse(os.path.join(ltf_path, ltf_file))
    root = tree.getroot()
    for doc in root:
        for text in doc:
            for seg in text:
                sent = seg.find("ORIGINAL_TEXT").text
                f.write(sent+'\n')
    f.close()

def run_semafor(semafor_sh_path, input_file, out_file, thread_num):
    cmd = [
        '/bin/bash',
        semafor_sh_path,
        input_file,
        out_file,
        str(thread_num)
    ]
    try:
        status = os.system(' '.join(cmd))
    except:
        print(' '.join(cmd))
        print("Unexpected error:", sys.exc_info())

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('language', type=str, help='language')
    parser.add_argument('ltf_path', type=str, help='ltf_path')
    # parser.add_argument('result_path', type=str, help='result_path')
    parser.add_argument('ltf_txt_path', type=str, help='ltf_txt_path')
    parser.add_argument('framenet_path', type=str, help='framenet_path')

    args = parser.parse_args()

    language = args.language
    ltf_path = args.ltf_path
    # result_path = args.result_path
    # ltf_txt_path = os.path.join(result_path, 'ltf_txt')
    # framenet_path = os.path.join(result_path, 'framenet_res')
    ltf_txt_path = args.ltf_txt_path
    framenet_path = args.framenet_path
    if not os.path.exists(ltf_txt_path):
        os.makedirs(ltf_txt_path)
    if not os.path.exists(framenet_path):
        os.makedirs(framenet_path)

    if language.startswith('en'):
        # thread_num = 2
        # semafor_sh_path = '/bin/runSemafor.sh'
        ltfs = os.listdir(ltf_path)
        for ltf_file in ltfs:
            doc_to_segment(ltf_path, ltf_file, ltf_txt_path)
            # one_line = ltf_file.replace(".ltf.xml", "")
            # if os.path.exists(os.path.join(framenet_path, one_line)):
            #     continue
            # run_semafor(semafor_sh_path, os.path.join(ltf_txt_path, one_line+'.ltf.txt'),
            #             os.path.join(framenet_path, one_line), thread_num)
