import spacy
import networkx as nx
import os
import sys
import time
import argparse
from collections import Counter
import logging
import numpy as np
import pickle
import time
from spacy.tokenizer import Tokenizer

def load_data(file):
    sentences = []
    relations = []
    e1_pos = []
    e2_pos = []
    en_type = []

    with open(file, 'r') as f:
        for line in f.readlines():
            all_features = line.strip().lower().split("\t")
            line = all_features[0].strip().split(" ")
            en_type.append(all_features[1].strip().split(" "))
            relations.append(int(line[0]))
            e1_pos.append((int(line[1]), int(line[2])))  # (start_pos, end_pos)
            e2_pos.append((int(line[3]), int(line[4])))  # (start_pos, end_pos)
            sentences.append(line[5:])
    return sentences, relations, e1_pos, e2_pos, en_type


def concat_str(sen_list):
    con_str = ""
    for word in sen_list:
        con_str += (word + " ")
    return con_str.strip()


def padding_list(old_list, max_len):
    if len(old_list) < max_len:
        new_list = old_list + [0]*(max_len - len(old_list))
    else:
        new_list = old_list[:max_len]
    return new_list


def save_pickle(conf_save, fpname):
    with open(fpname, "wb") as fmodel:
        pickle.dump(conf_save, fmodel)
    return None


def load_pickle(conf_name, fpname):
    with open(fpname, "rb") as fmodel:
        conf_name = pickle.load(fmodel)
    return conf_name


def build_dict(sentences):
    word_count = Counter()
    for sent in sentences:
        for w in sent:
            word_count[w] += 1

    ls = word_count.most_common()
    word_dict = {w[0]: index + 1 for (index, w) in enumerate(ls)}
    # leave 0 to PAD
    return word_dict


# build type dic, leave 0 to PAD
def build_type_dict(_list):
    type_dict = {}
    i = 1
    for subitem in _list:
        for item in subitem:
            if item not in type_dict:
                type_dict[item] = i
                i += 1
    return type_dict


def load_embedding(emb_file, emb_vocab, word_dict):
    vocab = {}
    with open(emb_vocab, 'r') as f:
        for id, w in enumerate(f.readlines()):
            w = w.strip().lower()
            vocab[w] = id

    f = open(emb_file, 'r')
    embed = f.readlines()

    dim = len(embed[0].split())
    num_words = len(word_dict) + 3
    embeddings = np.random.uniform(-0.01, 0.01, size=(num_words, dim))
    pre_trained = 0
    for w in vocab.keys():
        if w in word_dict:
            embeddings[word_dict[w]] = [float(x) for x in embed[vocab[w]].split()]
            pre_trained += 1
    embeddings[0] = np.zeros(dim)

    logging.info(
        'embeddings: %.2f%%(pre_trained) unknown: %d' % (pre_trained / num_words * 100, num_words - pre_trained))

    f.close()
    return embeddings.astype(np.float32)


def pos(x):
    '''
    map the relative distance between [0, 123)
    '''
    if x < -60:
        return 0
    if -60 <= x <= 60:
        return x + 61
    if x > 60:
        return 122


def shortest_dependency(intermediate_path, max_len):
    error = 0
    model = spacy.load('en_core_web_sm')
    custom_tokenizer = Tokenizer(model.vocab, {}, None, None, None)
    model.tokenizer = custom_tokenizer

    edges = []
    entity_offset = []
    out_features = []
    index = 0
    with open(intermediate_path) as fmodel:
        for line in fmodel:
            whole_sentence = line.strip().split("\t")[0]
            sen = whole_sentence.split(maxsplit=5)
            ori_sen = sen[5].strip()
            sentence = ori_sen.split(" ")
            entity_offset.append([int(sen[2]), int(sen[4])])
            parse_result = model(ori_sen)
            sub_graph = []
            sub_entity_concat = []
            token_concat = []
            features = []
            graph = None
            for token in parse_result:
                token_concat.append('{0}-{1}'.format(token.lower_, token.i))
                for child in token.children:
                    sub_graph.append(('{0}-{1}'.format(token.lower_, token.i),
                                      '{0}-{1}'.format(child.lower_, child.i)))
                if token.i in entity_offset[index]:
                    sub_entity_concat.append('{0}-{1}'.format(token.lower_, token.i))
                    assert token.lower_ == sentence[token.i].lower(), (sentence[token.i].lower(), token.lower_)
            edges.append(sub_graph)
            graph = nx.Graph(sub_graph)
            try:
                short_path = nx.shortest_path(graph, source=sub_entity_concat[0],
                                                      target=sub_entity_concat[1])
                # print(short_path)
                for word_concat in token_concat:
                    if word_concat in short_path:
                        features.append(1)
                    else:
                        features.append(0)
                        padding_list(features, max_len)
            except:
                features.extend([0] * max_len)
                features[int(sen[2]):int(sen[4])+1] = (int(sen[4])+1-int(sen[2])) * [1]
                error += 1
                # print(error)
            out_features.append(features)
            index += 1
            if index % 1000 == 0:
                print("extract %d sentences" % index)
    return out_features


def vectorize_position(sentence, max_len, e1_pos, e2_pos):
    # leave 123 as padding
    distance1 = [123] * max_len
    distance2 = [123] * max_len
    for i in range(min(len(sentence), max_len)):
        distance1[i] = pos(e1_pos[1] - i)
        distance2[i] = pos(e2_pos[1] - i)
    return distance1, distance2


def vectorize_type(type_dict, max_len, e1_pos, e2_pos, en_type):
    type_vec = [0] * max_len
    if e1_pos[1] < max_len:
        type_vec[e1_pos[1]] = type_dict[en_type[0]]
    if e2_pos[1] < max_len:
        type_vec[e2_pos[1]] = type_dict[en_type[1]]
    return type_vec


if __name__ == "__main__":
    ####################################################################################
    # feature extractor configuration files
    ####################################################################################
    feature_extractor_config = argparse.ArgumentParser(description='feature extraction')
    # training or testing data file path
    # /data/m1/shig4/AIDA/run/0913/en_asr/AIDA_plain_text.txt
    # feature flag
    feature_extractor_config.add_argument("--dp_name",
                                          type=str,
                                          default="dp.pkl",
                                          help="saved file name for dp features")
    feature_extractor_config.add_argument("--max_len",
                                          type=int,
                                          default=121,
                                          help="position embedding for entity2")

    feature_extractor_config.add_argument("--dependency",
                                          type=bool,
                                          default=True,
                                          help="shortest dependency feature")

    feature_extractor_config.add_argument("--converted_fpath",
                                          type=str,
                                          help="intermediate file path")

    feature_extractor_config.add_argument("--output_dir",
                                          type=str,
                                          help="feature results output dir")

    feature_params, _ = feature_extractor_config.parse_known_args()
    params, _ = feature_extractor_config.parse_known_args()

    if params.dependency:
        start = time.clock()
        out_dependency = shortest_dependency(params.converted_fpath, params.max_len)
        # print(out_dependency)
        save_pickle(out_dependency, os.path.join(params.output_dir, params.dp_name))
        end = time.clock()
        print(end-start)
