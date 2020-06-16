import codecs
import os
import argparse
import sys
import xml.etree.ElementTree as ET


def ltf2bio(ltf_str):
    doc_tokens = load_ltf(ltf_str)

    bio = []
    for sent in doc_tokens:
        sent_res = []
        for token in sent:
            t_text = token[0]
            if not t_text.strip():
                continue
            if t_text is None:
                t_text = ''
            t_doc_id = token[1]
            t_start_char = token[2]
            t_end_char = token[3]

            # get token bio tag
            sent_res.append(' '.join([t_text,
                                      '%s:%s-%s' % (t_doc_id,
                                                    t_start_char,
                                                    t_end_char)]))
        bio.append('\n'.join(sent_res))

    return '\n\n'.join(bio)


def load_ltf(ltf_str):
    doc_tokens = []
    root = ET.fromstring(ltf_str.encode('utf-8'))
    doc_id = root.find('DOC').get('id')
    for seg in root.find('DOC').find('TEXT').findall('SEG'):
        sent_tokens = []
        seg_text = seg.find('ORIGINAL_TEXT').text
        seg_start = int(seg.get('start_char'))
        seg_end = int(seg.get('end_char'))
        for token in seg.findall('TOKEN'):
            token_text = token.text
            start_char = int(token.get('start_char'))
            end_char = int(token.get('end_char'))

            assert seg_text[start_char-seg_start:end_char-seg_start+1] == token_text, \
                'ltf2bio load_ltf token offset error.'

            sent_tokens.append((token_text, doc_id, start_char, end_char))
        doc_tokens.append(sent_tokens)

    return doc_tokens


def write2file(bio_str, out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with codecs.open(out_file, 'w', 'utf-8') as f:
        f.write(bio_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ltf_input', type=str,
                        help='ltf input path')
    parser.add_argument('output', type=str,
                        help='output path')
    parser.add_argument('--ltf_filelist', type=str,
                        help='ltf filelist path')
    parser.add_argument('-s', '--separate_output',  action='store_true', default=False,
                        help='separate output')

    args = parser.parse_args()

    ltf_input = args.ltf_input
    output = args.output
    ltf_filelist = args.ltf_filelist
    separate_output = args.separate_output

    ltf_fp = []
    if os.path.isdir(ltf_input):
        if args.ltf_filelist:
            ltf_filelist = open(args.ltf_filelist).read().splitlines()
            ltf_fp = [os.path.join(ltf_input, item)
                      for item in ltf_filelist]
        else:
            ltf_fp = [os.path.join(ltf_input, item)
                      for item in os.listdir(args.ltf_input)
                      if '.ltf.xml' in item]
    else:
        ltf_fp = [ltf_input]

    res = []
    for i, filepath in enumerate(ltf_fp):
        assert os.path.exists(filepath)
        ltf_str = codecs.open(filepath, 'r', 'utf-8').read()
        bio_str = ltf2bio(ltf_str)
        if separate_output:
            out_file = os.path.join(
                output, os.path.basename(filepath).replace('.ltf.xml', '.bio')
            )
            write2file(bio_str, out_file)
        res.append(bio_str)

        sys.stdout.write('%d docs processed.\r' % i)
        sys.stdout.flush()

    if not separate_output:
        write2file('\n\n'.join(res), args.output)

    print('%d docs processed in total.' % len(ltf_fp))
