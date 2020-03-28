import sys
import os
import requests
# import subprocess
# from nominal_corefer_en import get_nominal_corefer
import json
import shutil
import codecs

PWD=os.path.dirname(os.path.abspath(__file__))

def edl(indir_ltf, indir_rsd, lang, outdir, edl_bio, edl_tab_nam, edl_tab_nom,
        edl_tab_pro, fine_grain_model):
    if os.path.exists(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir, exist_ok=True)

    # edl_tab_raw_nam = edl_tab_raw
    # edl_tab_raw_nom = edl_tab_raw.replace('.nam.','.nom.')
    # edl_tab_raw_pro = edl_tab_raw.replace('.nam.', '.pro.')

    url = 'http://0.0.0.0:5500/tagging'
    for doc_name_ltf in os.listdir(indir_ltf):
        print('processing %s' % doc_name_ltf)
        if not doc_name_ltf.endswith('.ltf.xml'):
            print('[ERROR] LTF file should be ended with .ltf.xml')
            continue
        try:
            ltf_str = codecs.open('%s/%s' % (indir_ltf, doc_name_ltf), encoding="utf-8").read()
            doc_id = doc_name_ltf.replace('.ltf.xml', '')
            rsd_str = codecs.open('%s/%s.rsd.txt' % (indir_rsd, doc_id), encoding="utf-8").read()
            input_data = {
                'ltf': ltf_str,
                'rsd': rsd_str,
                'doc_id': doc_id,
                'lang': lang
            }
            r = requests.post(url, data=input_data)
            if r.status_code != 200:
                continue
            ans = json.loads(r.text)
            with codecs.open(edl_bio, 'a', encoding="utf-8") as fw:
                bio_content = ans['bio']#.encode('utf-8')
                fw.write(bio_content)
                fw.write('\n')
            with codecs.open(edl_tab_nam, 'a', encoding="utf-8") as fw:
                if 'nam_tab' in ans:
                    fw.write(ans['nam_tab'])
                    fw.write('\n')
            with codecs.open(edl_tab_nom, 'a', encoding="utf-8") as fw:
                if 'nom_tab' in ans:
                    fw.write(ans['nom_tab'])
                    fw.write('\n')
            with codecs.open(edl_tab_pro, 'a', encoding="utf-8") as fw:
                if 'pro_tab' in ans:
                    fw.write(ans['pro_tab'])
                    fw.write('\n')
            # for line in ans['tab'].split('\n'):
            #     tmp = line.split('\t')
            #     if len(tmp) > 3:
            #         if tmp[6] == 'NAM':
            #             with codecs.open(edl_tab_raw_nam, 'a', encoding="utf-8") as fw:
            #                 fw.write('%s\n' % '\t'.join(tmp))
            #         elif tmp[6] == 'NOM':
            #             with codecs.open(edl_tab_raw_nom, 'a', encoding="utf-8") as fw:
            #                 fw.write('%s\n' % '\t'.join(tmp))
            #         elif tmp[6] == 'PRO':
            #             with codecs.open(edl_tab_raw_pro, 'a', encoding="utf-8") as fw:
            #                 fw.write('%s\n' % '\t'.join(tmp))
            with codecs.open(fine_grain_model, 'a', encoding="utf-8") as fw:
                fw.write(ans['tsv'])
                fw.write('\n')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = 'unexpected error: %s | %s | %s' % \
                  (exc_type, exc_obj, exc_tb.tb_lineno)
            print(msg)

    # # merge tabs
    # with open('%s/merged.tab' % outdir, 'w') as fw:
    #     for i in os.listdir(outdir):
    #         if not i.endswith('.ltf.xml.tab'):
    #             continue
    #         with open('%s/%s' % (outdir, i), 'r') as f:
    #             for line in f:
    #                 tmp = line.rstrip('\n').split('\t')
    #                 if len(tmp) > 3:
    #                     fw.write('%s\n' % '\t'.join(tmp))
    # cmd = [
    #     'rm',
    #     '%s/*.ltf.xml.tab' % outdir,
    # ]
    # subprocess.call(' '.join(cmd), shell=True)

    # # linking
    # url = 'http://0.0.0.0:3300/elisa_ie/entity_discovery_and_linking/en'
    # for i in os.listdir(indir):
    #     print('processing %s' % i)
    #     try:
    #         data = open('%s/%s' % (indir, i)).read()
    #         params = {
    #             'input_format': 'ltf',
    #             'output_format': 'EvalTab'
    #         }
    #         r = requests.post(url, data=data, params=params)
    #         if r.status_code != 200:
    #             continue
    #         with open('%s/%s.tab' % (outdir, i), 'w') as fw:
    #             fw.write(r.text.encode('utf-8'))
    #
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         msg = 'unexpected error: %s | %s | %s' % \
    #               (exc_type, exc_obj, exc_tb.tb_lineno)
    #         print(msg)

    # if use_nominal_corefer:
    #     # # nomincal coreference
    #     # dev = bio_path
    #     # dev_e = '%s/merged.tab' % outdir
    #     # out_e = '%s/merged_corefer.tab' % outdir
    #     get_nominal_corefer(edl_bio, edl_tab_raw, out_e=edl_tab)
    #     tab_final = edl_tab
    # else:
    #     tab_final = edl_tab_raw
    #
    # cmd = [
    #     'python',
    #     '%s/tab2cs.py' % PWD,
    #     tab_final,
    #     edl_cs_coarse,
    #     'EDL'
    # ]
    # subprocess.call(' '.join(cmd), shell=True)

if __name__ == '__main__':
    if len(sys.argv) < 10:
        print(sys.argv)
        print('USAGE: python <ltf input dir> <rsd input dir> <lang> '
              '<output dir> <bio output file> <tab output file (before coreference)> '
              '<tab output file (after coreference)> <cs output file> '
              '<fine_grain_model output file>')
        exit()
    indir_ltf= sys.argv[1]
    indir_rsd= sys.argv[2]
    lang= sys.argv[3]
    outdir = sys.argv[4]
    edl_bio = sys.argv[5]
    edl_tab_nam = sys.argv[6]
    edl_tab_nom = sys.argv[7]
    edl_tab_pro = sys.argv[8]
    # edl_tab = sys.argv[7]
    # edl_cs_coarse = sys.argv[8]
    fine_grain_model = sys.argv[9]
    # use_nominal_corefer = False
    # if len(sys.argv) == 11:
    #     if int(sys.argv[10]) > 0:
    #         use_nominal_corefer = True

    edl(indir_ltf, indir_rsd, lang, outdir, edl_bio, edl_tab_nam, edl_tab_nom,
        edl_tab_pro, fine_grain_model)
