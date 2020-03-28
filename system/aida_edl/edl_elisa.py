import sys
import os
import requests
import subprocess
from nominal_corefer_en import get_nominal_corefer
import json

PWD=os.path.dirname(os.path.abspath(__file__))

def edl(indir, bio_path, outdir):
    try:
        os.mkdir(outdir)
        print('mkdir ', outdir)
    except:
        pass

    url = 'http://0.0.0.0:3300/elisa_ie/entity_discovery_and_linking/en'
    for i in os.listdir(indir):
        print('processing %s' % i)
        try:
            data = open('%s/%s' % (indir, i)).read()
            params = {
                'input_format': 'ltf',
                'output_format': 'EvalTab'
            }
            r = requests.post(url, data=data, params=params)
            if r.status_code != 200:
                continue
            with open('%s/%s.tab' % (outdir, i), 'w') as fw:
                fw.write(r.text.encode('utf-8'))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            msg = 'unexpected error: %s | %s | %s' % \
                (exc_type, exc_obj, exc_tb.tb_lineno)
            print(msg)

    with open('%s/merged.tab' % outdir, 'w') as fw:
        for i in os.listdir(outdir):
            if not i.endswith('.ltf.xml.tab'):
                continue
            # tab = open('%s/%s' % (outdir, i), 'r').read()
            # if not tab:
            #     continue
            # fw.write(tab)
            # docid = i.replace('.ltf.xml.tab', '')
            with open('%s/%s' % (outdir, i), 'r') as f:
                for line in f:
                    tmp = line.rstrip('\n').split('\t')
                    if len(tmp) > 3:
                        fw.write('%s\n' % '\t'.join(tmp))
    cmd = [
        'rm',
        '%s/*.ltf.xml.tab' % outdir,
    ]
    subprocess.call(' '.join(cmd), shell=True)

    dev = bio_path
    dev_e = '%s/merged.tab' % outdir
    out_e = '%s/merged_corefer.tab' % outdir
    get_nominal_corefer(dev, dev_e, out_e=out_e)

    cmd = [
        'python',
        '%s/tab2cs.py' % PWD,
        '%s/merged_corefer.tab' % outdir,
        # '%s/merged.tab' % outdir,
        '%s/merged.cs' % outdir,
        'EDL'
    ]
    subprocess.call(' '.join(cmd), shell=True)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(sys.argv)
        print('USAGE: python <ltf input dir> <bio input dir> <output dir>')
        exit()
    indir = sys.argv[1]
    bio_path = sys.argv[2]
    outdir = sys.argv[3]
    edl(indir, bio_path, outdir)
