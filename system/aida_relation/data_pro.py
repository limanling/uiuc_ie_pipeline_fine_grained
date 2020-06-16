import numpy as np
import logging
from collections import Counter
import pickle
import io


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
def buildTypeDict(_list):
    type_dict = {}
    i = 1
    for subitem in _list:
        for item in subitem:
            if item not in type_dict:
                type_dict[item] = i
                i += 1
    return type_dict


def load_embedding(emb_file, word_dict):
    fin = io.open(emb_file, 'r', encoding='utf-8', newline='\n', errors='ignore')
    n, dim = map(int, fin.readline().split())
    vocab = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        vocab[tokens[0]] = list(map(float, tokens[1:]))

    num_words = len(word_dict) + 3
    embeddings = np.random.uniform(-0.01, 0.01, size=(num_words, dim))
    # embeddings[num_words-2] = np.random.uniform(-0.5, 0.5, size=(1, dim))
    # embeddings[num_words-1] = np.random.uniform(-0.5, 0.5, size=(1, dim))

    pre_trained = 0
    for w in word_dict.keys():
        if w in vocab:
            embeddings[word_dict[w]] = vocab[w]
            pre_trained += 1
    embeddings[0] = np.zeros(dim)

    logging.info(
        'embeddings: %.2f%%(pre_trained) unknown: %d' % (pre_trained / num_words * 100, num_words - pre_trained))
    fin.close()
    return embeddings.astype(np.float32)


def pos(x):
    '''
    map the relative distance between [0, 123)
    '''
    if x < -60:
        return 0
    if x >= -60 and x <= 60:
        return x + 61
    if x > 60:
        return 122


def vectorize_full(data, word_dict,type_dict, max_len=121, dp_fpath="./temp/dp.pkl"):
    sentences, relations, e1_pos, e2_pos, en_type = data
    # replace word with word-id
    # sents_vec = []
    e1_vec = []
    e2_vec = []

    num_data = len(sentences)
    sents_vec = np.zeros((num_data, max_len), dtype=int)
    en_type_vec = np.zeros((num_data, max_len), dtype=int)

    pool_mask_en1 = np.zeros((num_data, max_len), dtype=int)
    pool_mask = np.zeros((num_data, max_len), dtype=int)
    pool_mask_en2 = np.zeros((num_data, max_len), dtype=int)

    logging.debug('data shape: (%d, %d)' % (num_data, max_len))

    for idx, (sent, pos1, pos2) in enumerate(zip(sentences, e1_pos, e2_pos)):
        # UNK, PAD both use 0 as index
        vec = [word_dict[w] if w in word_dict else 0 for w in sent]
        if len(vec) > max_len:
            sents_vec[idx, :len(vec)] = vec[:max_len]
        else:
            sents_vec[idx, :len(vec)] = vec

        # last word of e1 and e2
        e1_vec.append(vec[pos1[1]])
        e2_vec.append(vec[pos2[1]])

        ################################
        # entity type embedding
        ################################
        if pos1[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos1[0]:pos1[1] + 1] = [type_dict[en_type[idx][0]]] * (pos1[1] + 1 - pos1[0])
        if pos2[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos2[0]:pos2[1] + 1] = [type_dict[en_type[idx][1]]] * (pos2[1] + 1 - pos2[0])

        ################################
        # mask for piece-wise pooling
        ################################
        pool_mask_en1[idx, :pos1[0]] = [1.0] * pos1[0]
        if pos2[1] < max_len:
            pool_mask[idx, pos1[0]:pos2[1] + 1] = [1.0] * (pos2[1] + 1 - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)
        else:
            pool_mask[idx, pos1[0]:] = [1.0] * (max_len - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)

    dist1 = []
    dist2 = []
    ######################
    # Position Embedding
    ######################
    for sent, p1, p2 in zip(sents_vec, e1_pos, e2_pos):
        # current word position - last word position of e1 or e2
        temp_pos1 = [pos(p1[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos1[p1[0]:p1[1] + 1] = [pos(0)] * (p1[1] + 1 - p1[0])
        dist1.append(temp_pos1)
        temp_pos2 = [pos(p2[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos2[p2[0]:p2[1] + 1] = [pos(0)] * (p2[1] + 1 - p2[0])
        dist2.append(temp_pos2)

    ######################
    # dependency features
    ######################
    dp_type_vec = np.zeros((num_data, max_len), dtype=int)
    dp_model = open(dp_fpath, "rb")
    dp_pickle = pickle.load(dp_model)
    index = 0
    for item in dp_pickle:
        if len(item) < max_len:
            dp_type_vec[index, :len(item)] = item
        else:
            dp_type_vec[index, :max_len] = item[:max_len]
        index += 1

    return sents_vec, relations, e1_vec, e2_vec, dist1, dist2, en_type_vec, dp_type_vec, pool_mask_en1, pool_mask, pool_mask_en2


def vectorize_cl(data, word_dict,type_dict, max_len=121):
    sentences, relations, e1_pos, e2_pos, en_type = data
    # replace word with word-id
    # sents_vec = []
    e1_vec = []
    e2_vec = []

    num_data = len(sentences)
    sents_vec = np.zeros((num_data, max_len), dtype=int)
    en_type_vec = np.zeros((num_data, max_len), dtype=int)

    pool_mask_en1 = np.zeros((num_data, max_len), dtype=int)
    pool_mask = np.zeros((num_data, max_len), dtype=int)
    pool_mask_en2 = np.zeros((num_data, max_len), dtype=int)

    logging.debug('data shape: (%d, %d)' % (num_data, max_len))

    for idx, (sent, pos1, pos2) in enumerate(zip(sentences, e1_pos, e2_pos)):
        # UNK, PAD both use 0 as index
        vec = [word_dict[w] if w in word_dict else 0 for w in sent]
        if len(vec) > max_len:
            sents_vec[idx, :len(vec)] = vec[:max_len]
        else:
            sents_vec[idx, :len(vec)] = vec

        # last word of e1 and e2
        e1_vec.append(vec[pos1[1]])
        e2_vec.append(vec[pos2[1]])

        ################################
        # entity type embedding
        ################################
        if pos1[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos1[0]:pos1[1] + 1] = [type_dict[en_type[idx][0]]] * (pos1[1] + 1 - pos1[0])
        if pos2[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos2[0]:pos2[1] + 1] = [type_dict[en_type[idx][1]]] * (pos2[1] + 1 - pos2[0])

        ################################
        # mask for piece-wise pooling
        ################################
        pool_mask_en1[idx, :pos1[0]] = [1.0] * pos1[0]
        if pos2[1] < max_len:
            pool_mask[idx, pos1[0]:pos2[1] + 1] = [1.0] * (pos2[1] + 1 - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)
        else:
            pool_mask[idx, pos1[0]:] = [1.0] * (max_len - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)

    dist1 = []
    dist2 = []
    ######################
    # Position Embedding
    ######################
    for sent, p1, p2 in zip(sents_vec, e1_pos, e2_pos):
        # current word position - last word position of e1 or e2
        temp_pos1 = [pos(p1[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos1[p1[0]:p1[1] + 1] = [pos(0)] * (p1[1] + 1 - p1[0])
        dist1.append(temp_pos1)
        temp_pos2 = [pos(p2[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos2[p2[0]:p2[1] + 1] = [pos(0)] * (p2[1] + 1 - p2[0])
        dist2.append(temp_pos2)
    return sents_vec, relations, e1_vec, e2_vec, dist1, dist2, en_type_vec, pool_mask_en1, pool_mask, pool_mask_en2


def vectorize_dp(data, word_dict, max_len, type_dict, dp_fpath):
    sentences, relations, e1_pos, e2_pos, en_type = data
    # replace word with word-id
    # sents_vec = []
    e1_vec = []
    e2_vec = []

    num_data = len(sentences)
    sents_vec = np.zeros((num_data, max_len), dtype=int)
    en_type_vec = np.zeros((num_data, max_len), dtype=int)

    logging.debug('data shape: (%d, %d)' % (num_data, max_len))

    for idx, (sent, pos1, pos2) in enumerate(zip(sentences, e1_pos, e2_pos)):
        # UNK, PAD both use 0 as index
        vec = [word_dict[w] if w in word_dict else 0 for w in sent]
        if len(vec) > max_len:
            sents_vec[idx, :len(vec)] = vec[:max_len]
        else:
            sents_vec[idx, :len(vec)] = vec

        # last word of e1 and e2
        e1_vec.append(vec[pos1[1]])
        e2_vec.append(vec[pos2[1]])

        ################################
        # entity type embedding
        ################################
        if pos1[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos1[0]:pos1[1] + 1] = [type_dict[en_type[idx][0]]] * (pos1[1] + 1 - pos1[0])
        if pos2[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos2[0]:pos2[1] + 1] = [type_dict[en_type[idx][1]]] * (pos2[1] + 1 - pos2[0])

    dist1 = []
    dist2 = []
    ######################
    # Position Embedding
    ######################
    for sent, p1, p2 in zip(sents_vec, e1_pos, e2_pos):
        # current word position - last word position of e1 or e2
        temp_pos1 = [pos(p1[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos1[p1[0]:p1[1] + 1] = [pos(0)] * (p1[1] + 1 - p1[0])
        dist1.append(temp_pos1)
        temp_pos2 = [pos(p2[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos2[p2[0]:p2[1] + 1] = [pos(0)] * (p2[1] + 1 - p2[0])
        dist2.append(temp_pos2)

    ######################
    # dependency features
    ######################
    dp_type_vec = np.zeros((num_data, max_len), dtype=int)
    dp_model = open(dp_fpath, "rb")
    dp_pickle = pickle.load(dp_model)
    index = 0
    for item in dp_pickle:
        if len(item) < max_len:
            dp_type_vec[index, :len(item)] = item
        else:
            dp_type_vec[index, :max_len] = item[:max_len]
        index += 1

    return sents_vec, relations, e1_vec, e2_vec, dist1, dist2, en_type_vec, dp_type_vec


def vectorize_mask(data, word_dict, max_len, type_dict):
    sentences, relations, e1_pos, e2_pos, en_type = data
    # replace word with word-id
    # sents_vec = []
    e1_vec = []
    e2_vec = []

    num_data = len(sentences)
    sents_vec = np.zeros((num_data, max_len), dtype=int)
    en_type_vec = np.zeros((num_data, max_len), dtype=int)

    pool_mask_en1 = np.zeros((num_data, max_len), dtype=int)
    pool_mask = np.zeros((num_data, max_len), dtype=int)
    pool_mask_en2 = np.zeros((num_data, max_len), dtype=int)

    logging.debug('data shape: (%d, %d)' % (num_data, max_len))

    for idx, (sent, pos1, pos2) in enumerate(zip(sentences, e1_pos, e2_pos)):
        # UNK, PAD both use 0 as index
        vec = [word_dict[w] if w in word_dict else 0 for w in sent]
        if len(vec) > max_len:
            sents_vec[idx, :len(vec)] = vec[:max_len]
        else:
            sents_vec[idx, :len(vec)] = vec

        # last word of e1 and e2
        e1_vec.append(vec[pos1[1]])
        e2_vec.append(vec[pos2[1]])

        ################################
        # entity type embedding
        ################################
        if pos1[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos1[0]:pos1[1] + 1] = [type_dict[en_type[idx][0]]] * (pos1[1] + 1 - pos1[0])
        if pos2[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos2[0]:pos2[1] + 1] = [type_dict[en_type[idx][1]]] * (pos2[1] + 1 - pos2[0])

        ################################
        # mask for piece-wise pooling
        ################################
        pool_mask_en1[idx, :pos1[0]] = [1.0] * pos1[0]
        if pos2[1] < max_len:
            pool_mask[idx, pos1[0]:pos2[1] + 1] = [1.0] * (pos2[1] + 1 - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)
        else:
            pool_mask[idx, pos1[0]:] = [1.0] * (max_len - pos1[0])
            pool_mask_en2[idx, pos2[1] + 1:] = [1.0] * (max_len - pos2[1] - 1)

    dist1 = []
    dist2 = []
    ######################
    # Position Embedding
    ######################
    for sent, p1, p2 in zip(sents_vec, e1_pos, e2_pos):
        # current word position - last word position of e1 or e2
        temp_pos1 = [pos(p1[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos1[p1[0]:p1[1] + 1] = [pos(0)] * (p1[1] + 1 - p1[0])
        dist1.append(temp_pos1)
        temp_pos2 = [pos(p2[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos2[p2[0]:p2[1] + 1] = [pos(0)] * (p2[1] + 1 - p2[0])
        dist2.append(temp_pos2)

    return sents_vec, relations, e1_vec, e2_vec, dist1, dist2, en_type_vec, pool_mask_en1, pool_mask, pool_mask_en2


def vectorize(data, word_dict, max_len, type_dict):
    sentences, relations, e1_pos, e2_pos, en_type = data
    # replace word with word-id
    # sents_vec = []
    e1_vec = []
    e2_vec = []

    num_data = len(sentences)
    sents_vec = np.zeros((num_data, max_len), dtype=int)
    en_type_vec = np.zeros((num_data, max_len), dtype=int)


    logging.debug('data shape: (%d, %d)' % (num_data, max_len))

    for idx, (sent, pos1, pos2) in enumerate(zip(sentences, e1_pos, e2_pos)):
        # UNK, PAD both use 0 as index
        vec = [word_dict[w] if w in word_dict else 0 for w in sent]
        if len(vec) > max_len:
            sents_vec[idx, :len(vec)] = vec[:max_len]
        else:
            sents_vec[idx, :len(vec)] = vec

        # last word of e1 and e2
        e1_vec.append(vec[pos1[1]])
        e2_vec.append(vec[pos2[1]])

        ################################
        # entity type embedding
        ################################
        if pos1[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos1[0]:pos1[1] + 1] = [type_dict[en_type[idx][0]]] * (pos1[1] + 1 - pos1[0])
        if pos2[1] < max_len:
            if en_type[idx][0] in type_dict:
                en_type_vec[idx, pos2[0]:pos2[1] + 1] = [type_dict[en_type[idx][1]]] * (pos2[1] + 1 - pos2[0])

    dist1 = []
    dist2 = []
    ######################
    # Position Embedding
    ######################
    for sent, p1, p2 in zip(sents_vec, e1_pos, e2_pos):
        # current word position - last word position of e1 or e2
        temp_pos1 = [pos(p1[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos1[p1[0]:p1[1] + 1] = [pos(0)] * (p1[1] + 1 - p1[0])
        dist1.append(temp_pos1)
        temp_pos2 = [pos(p2[1] - idx) for idx, _ in enumerate(sent)]
        if 0 < p1[1] < max_len:
            temp_pos2[p2[0]:p2[1] + 1] = [pos(0)] * (p2[1] + 1 - p2[0])
        dist2.append(temp_pos2)

    return sents_vec, relations, e1_vec, e2_vec, dist1, dist2, en_type_vec