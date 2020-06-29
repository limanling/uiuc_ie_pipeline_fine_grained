import sys
import os
import requests
# import subprocess
# from nominal_corefer_en import get_nominal_corefer
import json
import shutil
import codecs
import glob

PWD=os.path.dirname(os.path.abspath(__file__))

def edl(indir_ltf, indir_rsd, lang, edl_tab_nam, edl_tab_nom,
        edl_tab_pro, fine_grain_model, output_dir):

    url = 'http://0.0.0.0:5500/tagging'
    tab_filenames = {'nam_tab': edl_tab_nam, 'nom_tab': edl_tab_nom, 'pro_tab': edl_tab_pro}

    # if os.path.exists(outdir):
    #     shutil.rmtree(outdir)
    # os.makedirs(outdir, exist_ok=True)
    try:
        for tab_filetype in tab_filenames:
            os.remove(tab_filenames[tab_filetype].replace('.tab', '.bio'))
            os.remove(tab_filenames[tab_filetype])
        hid_fileList = glob.glob(os.path.join(output_dir, '*_hid.txt'))
        for filePath in hid_fileList:
                os.remove(filePath)
    except:
        pass


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
            # save bio
            for bio_filename in [edl_tab_nam, edl_tab_nom, edl_tab_pro]:
                with codecs.open(bio_filename.replace('.tab', '.bio'), 'a', encoding="utf-8") as fw:
                    bio_content = ans['bio']
                    fw.write(bio_content)
                    fw.write('\n')
            # save tab
            for tab_filetype in tab_filenames:
                with codecs.open(tab_filenames[tab_filetype], 'a', encoding="utf-8") as fw:
                    if tab_filetype in ans:
                        fw.write(ans[tab_filetype])
                        fw.write('\n')
            # save hidden vecs
            for hid_filetype in ['en_nam_hid', 'en_nom_5type_hid',
                                 'en_nom_wv_hid', 'en_pro_hid',
                                 'ru_nam_5type_hid', 'ru_nam_wv_hid',
                                 'uk_nam_5type_hid', 'uk_nam_wv_hid'
                                 ]:
                hid_filepath = os.path.join(output_dir, hid_filetype+'.txt')
                with codecs.open(hid_filepath, 'a', encoding="utf-8") as fw:
                    if hid_filetype in ans:
                        fw.write(ans[hid_filetype])
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
    print(sys.argv)
    if len(sys.argv) < 8:
        print('USAGE: python <ltf input dir> <rsd input dir> <lang> '
              '<tab output file (before coreference)> '
              '<tab output file (after coreference)> <cs output file> '
              '<fine_grain_model output file> <output_dir>')
        exit()
    indir_ltf= sys.argv[1]
    indir_rsd= sys.argv[2]
    lang= sys.argv[3]
    # outdir = sys.argv[4]
    # edl_bio = sys.argv[5]
    edl_tab_nam = sys.argv[4]
    edl_tab_nom = sys.argv[5]
    edl_tab_pro = sys.argv[6]
    # edl_tab = sys.argv[7]
    # edl_cs_coarse = sys.argv[8]
    fine_grain_model = sys.argv[7]
    output_dir = sys.argv[8]
    # use_nominal_corefer = False
    # if len(sys.argv) == 11:
    #     if int(sys.argv[10]) > 0:
    #         use_nominal_corefer = True

    edl(indir_ltf, indir_rsd, lang, edl_tab_nam, edl_tab_nom,
        edl_tab_pro, fine_grain_model, output_dir)
