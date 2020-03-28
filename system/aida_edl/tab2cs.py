import re
import sys
from collections import defaultdict


def read_tab(pdata, add_conf=False):
    res = {}
    res_etypes = defaultdict(lambda: defaultdict(int))
    with open(pdata, 'r') as f:
        for line in f:
            tmp = line.rstrip('\n').split('\t')
            # if len(tmp) != 8:
            #     continue
            mention = tmp[2]
            # Mention
            mention = mention.replace('\t', ' ') \
                             .replace('\n', ' ') \
                             .replace('\r', ' ')
            mention = mention.replace('"', ' ') # remove Double quotes
            offset = tmp[3]
            docid = re.match('(.+):(\d+)-(\d+)', offset).group(1)
            kbid = tmp[4]
            # if kbid.startswith('NIL'):
            kbid = '%s_%s' % (kbid, docid)
            etype = tmp[5]
            mtype = tmp[6]
            if add_conf:
                conf = tmp[7]
            else:
                conf = 1.0

            if kbid not in res:
                res[kbid] = {}
            if docid not in res[kbid]:
                res[kbid][docid] = []
            res[kbid][docid].append((mention, offset, etype, mtype, conf))
            res_etypes[kbid][etype] += 1

    return res, res_etypes


def process(p_tab, p_out, prefix):
    data, etypes = read_tab(p_tab, add_conf=True)
    out = open(p_out, 'w')
    count = 0

    runid = 'RPI_BLENDER1'
    out.write(runid + '\n\n')

    eid2kbid = {}
    for kbid in sorted(data):
        entity_id = ':Entity_{number:0{width}d}'.format(width=7, number=count)
        entity_id = entity_id.replace(':Entity_', ':Entity_%s_' % prefix)
        etype = sorted(etypes[kbid].items(), key=lambda x: x[1], reverse=True)[0][0]
        out.write('%s\ttype\t%s\n' % (entity_id, etype))
        for docid in data[kbid]:
            # Canonical Mention
            mentions = sorted(data[kbid][docid],
                              key=lambda x: len(x[0]), reverse=True)
            found = False
            for m in mentions:
                if m[3] == 'NAM':
                    canonical_men = m
                    found = True
                    break
            try:
                assert found
            except:
                canonical_men = mentions[0]
            out.write('%s\tcanonical_mention\t"%s"\t%s\t%s\n' % (entity_id,
                                                                 canonical_men[0],
                                                                 canonical_men[1],
                                                                 canonical_men[4]))
            for men in mentions:
                if men[3] == 'PRO':
                    mtype = 'pronominal_mention'
                elif men[3] == 'NOM':
                    mtype = 'nominal_mention'
                else:
                    assert men[3] == 'NAM'
                    mtype = 'mention'
                out.write('%s\t%s\t"%s"\t%s\t%s\n' % (entity_id,
                                                      mtype,
                                                      men[0],
                                                      men[1],
                                                      men[4]))
        out.write('%s\tlink\t%s\n' % (entity_id, kbid))
        count += 1

    out.close()


def check(pdata):
    res = set()
    data = open(pdata, 'r').read()
    docids = re.findall('(\S+):(\d+)-(\d+)', data)
    for i in docids:
        docid = i[0]
        res.add(docid)
    print(len(res))


if __name__ == '__main__':
    ptab = sys.argv[1]
    outpath = sys.argv[2]
    prefix = sys.argv[3]
    process(ptab, outpath, prefix)

