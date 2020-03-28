import requests
import os
import json
import argparse
import io
import shutil

def get_nominal_corefer(dev, dev_e, dev_f=None, out_e=None):
    print('Loading tagged docs from %s...' % dev)
    dev = io.open(dev, 'r').read().split("\n")
    while len(dev[-1]) == 0:
        dev = dev[:-1]
    print('Loading lorelei edl mentions from %s...' % dev_e)
    dev_e = io.open(dev_e, 'r').read().split("\n")
    while len(dev_e[-1]) == 0:
        dev_e = dev_e[:-1]
    if dev_f is not None and dev_f != "":
        print('Loading freebase edl mentions from %s...' % dev_f)
        dev_f = io.open(dev_f, 'r').read().split("\n")
        while len(dev_f[-1]) == 0:
            dev_f = dev_f[:-1]
    else:
        dev_f = None
    result = {'dev': dev, 'dev_e': dev_e, 'dev_f': dev_f}
    json_string = json.dumps(result)
    r = requests.post('http://127.0.0.1:2468/aida_nominal_coreference_en', json=json_string)
    if r.status_code == 200:
        print("Succeed coreference")
        f = io.open(out_e, 'w')
        f.write(r.text)
        f.close()
    else:
        print(r.status_code)

if __name__ == '__main__':
    # Read parameters from command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev", default="data/en.bio",
        help="Input bio location"
    )
    parser.add_argument(
        "--dev_e", default="data/en.linking.tab",
        help="Input lorelei edl location"
    )
    parser.add_argument(
        "--dev_f", default="",
        help="Input freebase edl location"
    )
    parser.add_argument(
        "--out_e", default="en.linking.tab",
        help="Output edl location"
    )
    parser.add_argument(
        "--use_nominal_corefer", type=int, default=1,
        help="Use nominal coreference or not. If not, just copy the original *.tab as as final tab."
    )
    args = parser.parse_args()

    if args.use_nominal_corefer == 0:
        # If not use_nominal_coreference, just copy the original *.tab as as final tab.
        shutil.copy(args.dev_e, args.out_e)
    else:
        get_nominal_corefer(args.dev, args.dev_e, args.dev_f, args.out_e)
