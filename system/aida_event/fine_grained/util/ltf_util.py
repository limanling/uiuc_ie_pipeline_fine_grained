import xml.etree.ElementTree as ET
import os


def parse_offset_str(offset_str):
    docid = offset_str[:offset_str.find(':')]
    start = int(offset_str[offset_str.find(':') + 1:offset_str.find('-')])
    end = int(offset_str[offset_str.find('-') + 1:])
    return docid, start, end

class LTF_util(object):
    def __init__(self, ltf_dir):
        super(LTF_util, self).__init__()
        self.ltf_dir = ltf_dir

    def parse_offset_str(self, offset_str):
        return parse_offset_str(offset_str)

    def get_context(self, offset_str):
        docid, start, end = self.parse_offset_str(offset_str)

        tokens = []

        ltf_file_path = os.path.join(self.ltf_dir, docid + '.ltf.xml')
        if not os.path.exists(ltf_file_path):
            return '[ERROR]NoLTF %s' % docid
        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    seg_beg = int(seg.attrib["start_char"])
                    seg_end = int(seg.attrib["end_char"])
                    if start >= seg_beg and end <= seg_end:
                        for token in seg:
                            if token.tag == "TOKEN":
                                tokens.append(token.text)
                    if len(tokens) > 0:
                        return tokens
        return tokens

    def get_expand_text(self, offset_str, window):
        docid, start, end = self.parse_offset_str(offset_str)

        tokens = []

        ltf_file_path = os.path.join(self.ltf_dir, docid + '.ltf.xml')
        if not os.path.exists(ltf_file_path):
            return '[ERROR]NoLTF %s' % docid
        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    seg_beg = int(seg.attrib["start_char"])
                    seg_end = int(seg.attrib["end_char"])
                    # print(seg, len(seg))
                    if start >= seg_beg and end <= seg_end:
                        max_token_id = 0
                        min_token_id = 1000
                        for i in range(len(seg)):
                            token = seg[i]
                            if token.tag == "TOKEN":
                                token_id = int(token.attrib["id"].split('-')[-1])
                                token_beg = int(token.attrib["start_char"])
                                token_end = int(token.attrib["end_char"])
                                tokens.append(token.text)
                                # print(start, end, token_beg, token_end)
                                if start <= token_beg and end >= token_end:
                                    if token_id >= max_token_id:
                                        max_token_id = token_id
                                    if token_id <= min_token_id:
                                        min_token_id = token_id
                        # print(max_token_id, min_token_id, start, end)
                    if len(tokens) > 0:
                        window_left = max(0, min_token_id-window)
                        window_right = min(len(seg), max_token_id+window+1)
                        # print(window_left, window_right)
                        # print(tokens[window_left: window_right])
                        return tokens[window_left: window_right]
        return None

    def get_context_html(self, offset_str):
        docid, start, end = self.parse_offset_str(offset_str)

        tokens = []

        ltf_file_path = os.path.join(self.ltf_dir, docid + '.ltf.xml')
        if not os.path.exists(ltf_file_path):
            return '[ERROR]NoLTF %s' % docid
        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    seg_beg = int(seg.attrib["start_char"])
                    seg_end = int(seg.attrib["end_char"])
                    if start >= seg_beg and end <= seg_end:
                        for token in seg:
                            if token.tag == "TOKEN":
                                token_text = token.text
                                token_beg = int(token.attrib["start_char"])
                                token_end = int(token.attrib["end_char"])
                                if start <= token_beg and end >= token_end:
                                    token_text = '<span style="color:blue">' + token_text + '</span>'
                                tokens.append(token_text)
                    if len(tokens) > 0:
                        return ' '.join(tokens)
        return '[ERROR]'


    def get_str(self, offset_str):
        docid, start, end = self.parse_offset_str(offset_str)

        tokens = []

        ltf_file_path = os.path.join(self.ltf_dir, docid + '.ltf.xml')
        if not os.path.exists(ltf_file_path):
            return '[ERROR]NoLTF %s' % docid
        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    for token in seg:
                        if token.tag == "TOKEN":
                            # print(token.attrib["start_char"])
                            token_beg = int(token.attrib["start_char"])
                            token_end = int(token.attrib["end_char"])
                            if start <= token_beg and end >= token_end:
                                tokens.append(token.text)
        if len(tokens) > 0:
            return ' '.join(tokens)
        print('[ERROR]can not find the string with offset ', offset_str)
        return None

    def get_str_inside_sent(self, offset_str):
        docid, start, end = self.parse_offset_str(offset_str)

        tokens = []

        ltf_file_path = os.path.join(self.ltf_dir, docid + '.ltf.xml')
        if not os.path.exists(ltf_file_path):
            return '[ERROR]NoLTF %s' % docid
        tree = ET.parse(ltf_file_path)
        root = tree.getroot()
        for doc in root:
            for text in doc:
                for seg in text:
                    seg_beg = int(seg.attrib["start_char"])
                    seg_end = int(seg.attrib["end_char"])
                    if start >= seg_beg and end <= seg_end:
                        for token in seg:
                            if token.tag == "TOKEN":
                                # print(token.attrib["start_char"])
                                token_beg = int(token.attrib["start_char"])
                                token_end = int(token.attrib["end_char"])
                                if start <= token_beg and end >= token_end:
                                    tokens.append(token.text)
                    if len(tokens) > 0:
                        return ' '.join(tokens)
        print('[ERROR]can not find the string with offset ', offset_str)
        return None


if __name__ == '__main__':
    ltf_dir = '/data/m1/lim22/aida2019/LDC2019E42/source/en_all'
    ltf_util = LTF_util(ltf_dir)
    # print(ltf_util.get_context('HC0005KMS:934-939'))
    print(ltf_util.get_expand_text('HC0005QCD:140-149', 2))