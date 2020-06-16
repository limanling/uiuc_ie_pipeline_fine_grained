import spacy
from utils.aida2inter import *
import time
import os
import networkx as nx
from utils.feature_extraction import padding_list
import pickle
import numpy as np
import torch
import torch.utils.data as D
import utils.data_pro as pro
from torch.autograd import Variable
import torch.nn.functional as F
from utils.generate_CS import rel_map_ERE, ERE_to_AIDA_final_ouput, generate_cs_file


def save_pickle(conf_save, fpname):
    with open(fpname, "wb") as fmodel:
        pickle.dump(conf_save, fmodel)
    return None


def data_unpack_full(cat_data, target, max_len=121):
    list_x = np.split(cat_data.numpy(),
                      [max_len, max_len * 2, max_len * 3, max_len * 4, max_len * 5, max_len * 6, max_len * 7],
                      1)
    bx = Variable(torch.from_numpy(list_x[0]))
    bd1 = Variable(torch.from_numpy(list_x[1]))
    bd2 = Variable(torch.from_numpy(list_x[2]))
    b_en = Variable(torch.from_numpy(list_x[3]))
    b_dp = Variable(torch.from_numpy(list_x[4].astype(np.float32)))
    b_mask_e1 = Variable(torch.from_numpy(list_x[5].astype(np.float32)), requires_grad=False)
    b_mask_e1_e2 = Variable(torch.from_numpy(list_x[6].astype(np.float32)), requires_grad=False)
    b_mask_e2 = Variable(torch.from_numpy(list_x[7].astype(np.float32)), requires_grad=False)
    target = Variable(target)
    return bx, bd1, bd2, b_en, b_dp, b_mask_e1, b_mask_e1_e2, b_mask_e2, target


def data_unpack_cl(cat_data, target, max_len=121):
    list_x = np.split(cat_data.numpy(),
                      [max_len, max_len * 2, max_len * 3, max_len * 4, max_len * 5, max_len * 6],
                      1)
    bx = Variable(torch.from_numpy(list_x[0]))
    bd1 = Variable(torch.from_numpy(list_x[1]))
    bd2 = Variable(torch.from_numpy(list_x[2]))
    b_en = Variable(torch.from_numpy(list_x[3]))
    b_mask_e1 = Variable(torch.from_numpy(list_x[4].astype(np.float32)), requires_grad=False)
    b_mask_e1_e2 = Variable(torch.from_numpy(list_x[5].astype(np.float32)), requires_grad=False)
    b_mask_e2 = Variable(torch.from_numpy(list_x[6].astype(np.float32)), requires_grad=False)
    target = Variable(target)
    return bx, bd1, bd2, b_en, b_mask_e1, b_mask_e1_e2, b_mask_e2, target


def json2inter(edl_tab_string, ltf_json_dic, max_len=121):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    start_time = time.clock()
    doc2mention, mention2type = doc_to_men_to_type(edl_tab_string)
    doc2segment, docseg2mention, doc2segtext, doc2segoffset = doc_to_segment(doc2mention, ltf_json_dic)
    error = 0
    with open("temp/AIDA_plain_text.txt", "w") as fmodel:
        for doc_id in docseg2mention:
            for segment in docseg2mention[doc_id]:
                list_offset = []
                for i in range(len(docseg2mention[doc_id][segment])):
                    if docseg2mention[doc_id][segment][i] in doc2segoffset[doc_id][segment]:
                        mention_loffset = doc2segoffset[doc_id][segment].index(docseg2mention[doc_id][segment][i])
                        list_offset.append([mention_loffset, mention_loffset])
                    else:
                        temp = []
                        for j in range(len(doc2segoffset[doc_id][segment])):
                            if docseg2mention[doc_id][segment][i][0] in doc2segoffset[doc_id][segment][j]:
                                temp.append(j)
                            if docseg2mention[doc_id][segment][i][1] in doc2segoffset[doc_id][segment][j]:
                                temp.append(j)
                        list_offset.append(temp)
                list_offset = sorted(list_offset)
                out_list = assembly_list(list_offset)
                if out_list:
                    for item in out_list:
                        if len(doc2segtext[doc_id][segment]) < max_len:
                            try:
                                ltf_mention1 = doc_id + ":" + doc2segoffset[doc_id][segment][item[0][0]][0] + "-" + \
                                           doc2segoffset[doc_id][segment][item[0][1]][1]
                                ltf_mention2 = doc_id + ":" + doc2segoffset[doc_id][segment][item[1][0]][0] + "-" + \
                                           doc2segoffset[doc_id][segment][item[1][1]][1]
                            except:
                                print(doc_id)
                                error += 1
                                continue
                            output_sentence = ""
                            for word in doc2segtext[doc_id][segment]:
                                output_sentence += (word + " ")
                            output_seg = doc_id + ":" + str(doc2segment[doc_id][segment][0]) + "-" + \
                                         str(doc2segment[doc_id][segment][1])
                            output_sentence = output_sentence.strip()
                            if item[0][1] != item[1][0]:
                                fmodel.write("1" + " " + str(item[0][0]) + " " + str(item[0][1]) + " " +
                                         str(item[1][0]) + " " + str(item[1][1]) + " "
                                         + output_sentence + "\t" + mention2type[ltf_mention1] + " " + mention2type[
                                             ltf_mention2]
                                         + "\t" + ltf_mention1 + " " + ltf_mention2 + "\t" + output_seg + "\n")
                # # find back the ltf offset
    end_time = time.clock()
    print("Preprocess running time is: %s" % str(end_time - start_time))
    return True


def extract_shortest_path(model, intermediate_path="temp/AIDA_plain_text.txt", max_len=121):
    error = 0
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
    save_pickle(out_features, "temp/dp.pkl")
    return True


def extract_relations(model, word_dict, type_dic, test_file="temp/AIDA_plain_text.txt", batch_size=64):
    t_data = pro.load_data(test_file)
    t_x, t_y, t_e1, t_e2, t_dist1, t_dist2, t_en_type_vec, t_dp_vec, t_pool_mask_e1, \
    t_pool_mask, t_pool_mask_e2 = pro.vectorize_full(t_data, word_dict, type_dic)
    t_y = np.array(t_y).astype(np.int64)
    t_np_cat = np.concatenate((t_x, np.array(t_dist1), np.array(t_dist2), np.array(t_en_type_vec), np.array(t_dp_vec),
                               np.array(t_pool_mask_e1), np.array(t_pool_mask), np.array(t_pool_mask_e2)),
                              1)
    test = torch.from_numpy(t_np_cat.astype(np.int64))
    t_y_tensor = torch.from_numpy(t_y)
    test_datasets = D.TensorDataset(data_tensor=test, target_tensor=t_y_tensor)
    test_dataloader = D.DataLoader(test_datasets, batch_size, False, num_workers=1)

    results = []
    confidence_score = []

    for (b_x_cat, b_y) in test_dataloader:
        bx, bd1, bd2, ben, bdp, bmask1, bmask, bmask2, by = data_unpack_full(b_x_cat, b_y)
        logits = model(bx, bd1, bd2, ben, bdp, bmask1, bmask, bmask2, False)
        score = torch.nn.functional.softmax(logits, 1).data
        predict = torch.max(logits, 1)[1].data
        temp = []
        for idx in range(predict.size()[0]):
            temp.append(score[idx][predict[idx]])
        results.append(predict)
        confidence_score.append(temp)
    with open("temp/AIDA_results.txt", "w") as fmodel:
        for result, score in zip(results, confidence_score):
            for idx, rel in enumerate(result):
                fmodel.write(str(rel) + "\t" + str(score[idx]) + "\n")

    print("test done!")
    return True


def extract_relations_cl(model, word_dict, type_dic, test_file="temp/AIDA_plain_text.txt", batch_size=64):
    t_data = pro.load_data(test_file)
    t_x, t_y, t_e1, t_e2, t_dist1, t_dist2, t_en_type_vec, t_pool_mask_e1, \
    t_pool_mask, t_pool_mask_e2 = pro.vectorize_cl(t_data, word_dict, type_dic)
    t_y = np.array(t_y).astype(np.int64)
    t_np_cat = np.concatenate((t_x, np.array(t_dist1), np.array(t_dist2), np.array(t_en_type_vec),
                               np.array(t_pool_mask_e1), np.array(t_pool_mask), np.array(t_pool_mask_e2)),
                              1)
    test = torch.from_numpy(t_np_cat.astype(np.int64))
    t_y_tensor = torch.from_numpy(t_y)
    test_datasets = D.TensorDataset(data_tensor=test, target_tensor=t_y_tensor)
    test_dataloader = D.DataLoader(test_datasets, batch_size, False, num_workers=1)

    results = []
    confidence_score = []

    for (b_x_cat, b_y) in test_dataloader:
        bx, bd1, bd2, ben, bmask1, bmask, bmask2, by = data_unpack_cl(b_x_cat, b_y)
        logits = model(bx, bd1, bd2, ben, bmask1, bmask, bmask2, False)
        score = torch.nn.functional.softmax(logits, 1).data
        predict = torch.max(logits, 1)[1].data
        temp = []
        for idx in range(predict.size()[0]):
            temp.append(score[idx][predict[idx]])
        results.append(predict)
        confidence_score.append(temp)
    with open("temp/results_post_sponsor.txt", "w") as fmodel:
        for result, score in zip(results, confidence_score):
            for idx, rel in enumerate(result):
                fmodel.write(str(rel) + "\t" + str(score[idx]) + "\n")

    print("test done!")
    return True


def concat_item(l_list):
    out_string = ""
    for item in l_list:
        out_string += (item + " ")
    return out_string.strip()


def load_model(train_file="data/ere_filtered_train.txt", eval_file="data/ere_filtered_test.txt",
                      model_path="data/filter_ere_dp_mask_5000.636.pkl"):
    data = pro.load_data(train_file)
    e_data = pro.load_data(eval_file)
    word_dict = pro.build_dict(data[0] + e_data[0])
    entype_dict = pro.buildTypeDict(data[4] + e_data[4])
    neural_model = torch.load(model_path, map_location={'cuda:0': 'cpu'})
    return word_dict, entype_dict, neural_model


def load_ru(train_file="data/convert_ere_ru_train.txt", eval_file="data/convert_ere_ru_test.txt",
                      model_path="data/ru_new_piece_5000.724.pkl"):
    data = pro.load_data(train_file)
    e_data = pro.load_data(eval_file)
    word_dict = pro.build_dict(data[0] + e_data[0])
    entype_dict = pro.buildTypeDict(data[4] + e_data[4])
    neural_model = torch.load(model_path, map_location={'cuda:0': 'cpu'})
    return word_dict, entype_dict, neural_model


def load_uk(train_file="data/convert_ere_uk_train.txt", eval_file="data/convert_ere_uk_test.txt",
                      model_path="data/uk_new_piece_5000.682.pkl"):
    data = pro.load_data(train_file)
    e_data = pro.load_data(eval_file)
    word_dict = pro.build_dict(data[0] + e_data[0])
    entype_dict = pro.buildTypeDict(data[4] + e_data[4])
    neural_model = torch.load(model_path, map_location={'cuda:0': 'cpu'})
    return word_dict, entype_dict, neural_model


def post_processing(train_file="data/ere_filtered_train.txt", plain_text = "temp/AIDA_plain_text.txt",
                    results="temp/AIDA_results.txt", pattern_file="data/ere_pattern.txt", other_label="32"):
    ####################################
    # counting entity type constraints
    ####################################

    rel2type = {}
    with open(train_file) as fmodel:
        for line in fmodel:
            whole = line.strip().split("\t")
            en_type = whole[1].strip().split(" ")
            en_type[0] = en_type[0].strip()
            en_type[1] = en_type[1].strip()
            rel = whole[0].strip().split(" ", 1)[0].strip()
            if rel not in rel2type:
                rel2type[rel] = [rel2type]
            else:
                if en_type not in rel2type[rel]:
                    rel2type[rel].append(en_type)

    relation_patterns = {}
    ere_rel_type_dic = {'physical_locatednear(Arg-1,Arg-2)': 0,
                        'physical_locatednear(Arg-2,Arg-1)': 1,
                        'physical_resident(Arg-1,Arg-2)': 2,
                        'physical_resident(Arg-2,Arg-1)': 3,
                        'physical_orgheadquarter(Arg-1,Arg-2)': 4,
                        'physical_orgheadquarter(Arg-2,Arg-1)': 5,
                        'physical_orglocationorigin(Arg-1,Arg-2)': 6,
                        'physical_orglocationorigin(Arg-2,Arg-1)': 7,
                        'partwhole_subsidiary(Arg-1,Arg-2)': 8,
                        'partwhole_subsidiary(Arg-2,Arg-1)': 9,
                        'partwhole_membership(Arg-1,Arg-2)': 10,
                        'partwhole_membership(Arg-2,Arg-1)': 11,
                        'personalsocial_business(Arg-1,Arg-2)': 12,
                        'personalsocial_business(Arg-2,Arg-1)': 12,
                        'personalsocial_family(Arg-1,Arg-2)': 13,
                        'personalsocial_family(Arg-2,Arg-1)': 13,
                        'personalsocial_unspecified(Arg-1,Arg-2)': 14,
                        'personalsocial_unspecified(Arg-2,Arg-1)': 14,
                        'personalsocial_role(Arg-1,Arg-2)': 15,
                        'personalsocial_role(Arg-2,Arg-1)': 15,
                        'orgaffiliation_employmentmembership(Arg-1,Arg-2)': 16,
                        'orgaffiliation_employmentmembership(Arg-2,Arg-1)': 17,
                        'orgaffiliation_leadership(Arg-1,Arg-2)': 18,
                        'orgaffiliation_leadership(Arg-2,Arg-1)': 19,
                        'orgaffiliation_investorshareholder(Arg-1,Arg-2)': 20,
                        'orgaffiliation_investorshareholder(Arg-2,Arg-1)': 21,
                        'orgaffiliation_studentalum(Arg-1,Arg-2)': 22,
                        'orgaffiliation_studentalum(Arg-2,Arg-1)': 23,
                        'orgaffiliation_ownership(Arg-1,Arg-2)': 24,
                        'orgaffiliation_ownership(Arg-2,Arg-1)': 25,
                        'orgaffiliation_founder(Arg-1,Arg-2)': 26,
                        'orgaffiliation_founder(Arg-2,Arg-1)': 27,
                        'generalaffiliation_more(Arg-1,Arg-2)': 28,
                        'generalaffiliation_more(Arg-2,Arg-1)': 29,
                        'generalaffiliation_opra(Arg-1,Arg-2)': 30,
                        'generalaffiliation_opra(Arg-2,Arg-1)': 31,
                        'NO-RELATION(Arg-1,Arg-1)': 32,
                        'generalaffiliation_apora(Arg-1,Arg-2)': 33,
                        'generalaffiliation_apora(Arg-2,Arg-1)': 34,
                        'sponsorship(Arg-1,Arg-2)': 35,
                        'sponsorship(Arg-2,Arg-1)': 36,
                        }
    label = []
    score = []
    with open(results) as fmodel:
        for line in fmodel:
            temp = line.strip().split("\t")
            label.append(temp[0].strip())
            score.append(temp[1].strip())

    with open(pattern_file) as fmodel:
        for line in fmodel:
            whole = line.strip().split("\t")
            if whole[0].strip() not in relation_patterns:
                relation_patterns[whole[0].strip()] = [whole[1].strip()]
            else:
                relation_patterns[whole[0].strip()].append(whole[1].strip())
    line_index = 0
    fixed_type_num = 0
    rel_num = 0
    with open(plain_text) as fmodel:
        for line in fmodel:
            temp = line.strip().split("\t")
            temp_whole = temp[0].strip().split(" ", 5)
            mention1_offset = int(temp_whole[2].strip())
            mention2_offset = int(temp_whole[3].strip())
            relation = temp_whole[0].strip()
            e1_type, e2_type = temp[1].strip().split(" ")
            en_type = [e1_type.strip(), e2_type.strip()]
            whole_sentence = temp_whole[5].strip().split(" ")
            pattern = e1_type + " " + concat_item(whole_sentence[mention1_offset + 1: mention2_offset]) + " " + e2_type
            try:
                extend_pattern = whole_sentence[mention1_offset - 1] + " " + pattern
            except:
                extend_pattern = None
            # filter results by extracted patterns and extended patterns
            for key in relation_patterns:
                if pattern in relation_patterns[key]:
                    label[line_index] = str(ere_rel_type_dic[key])
                if extend_pattern in relation_patterns[key]:
                    label[line_index] = str(ere_rel_type_dic[key])
            # filter results by type constraints
            try:
                if en_type not in rel2type[label[line_index]] and label[line_index] != other_label:
                    label[line_index] = other_label
                    fixed_type_num += 1
            except:
                continue
            if label[line_index] != other_label:
                rel_num += 1
            line_index += 1
            ##############
            # Sponsor relation
            ##############

    with open("temp/results_post.txt", "w", encoding="utf-8") as fmodel:
        for i, item in enumerate(label):
            fmodel.write(item + "\t" + score[i] + "\n")
    print("fixed num is %d" % fixed_type_num)
    print("relation num is %d" % rel_num)
    return True


def extract_sponsor(spacy_model, plain_text="temp/AIDA_plain_text.txt", post_result="temp/results_post.txt",
                    sponsor_patterns="data/sponsor_patterns",other_label="32", sponsor_label="35", constrain_length=10, ):
    feature_set = []
    sim_feature_set = []
    with open(sponsor_patterns) as fmodel:
        for line in fmodel:
            feature_set.append(" " + line.strip())
            sim_feature_set.append(line.strip().lower())
    type_constraint = ["ORG", "GPE", "LOC"]
    ####################################
    # counting entity type constraints
    ####################################
    label = []
    score = []
    sen_list = []
    index_list = []
    with open(post_result) as fmodel:
        for line in fmodel:
            temp = line.strip().split("\t")
            label.append(temp[0].strip())
            score.append(temp[1].strip())
    num = 0
    label_index = 0

    with open(plain_text) as fmodel:
        for line in fmodel:
            temp = line.strip().split("\t")
            temp_whole = temp[0].strip().split(" ", 5)
            mention1_offset = int(temp_whole[2].strip())
            mention2_offset = int(temp_whole[3].strip())
            relation = temp_whole[0].strip()
            e1_type, e2_type = temp[1].strip().split(" ")
            en_type = [e1_type.strip(), e2_type.strip()]
            whole_sentence = temp_whole[5].strip().split(" ")
            pattern = e1_type + " " + concat_item(whole_sentence[mention1_offset + 1: mention2_offset]) + " " + e2_type
            if e1_type in type_constraint and e2_type in type_constraint and label[label_index] == other_label and (
                    mention2_offset - mention1_offset) < constrain_length:
                flag = False
                whole_span = " " + concat_item(whole_sentence[mention1_offset + 1: mention2_offset])
                for item in feature_set:
                    if item in whole_span:
                        # for item in concat_item(whole_sentence[mention1_offset + 1: mention2_offset]):
                        #     if item in feature_set:
                        flag = True
                        break
                if flag and "in order to" not in whole_span:
                    # if shortest_dependency_length(line) < 5:
                    sen_list.append(line)
                    index_list.append(label_index)
                    num += 1
            label_index += 1
    print(num)
    filter_num = 0
    for j, line in enumerate(sen_list):
        edges = []
        entity_offset = []
        index = 0
        whole_sen = line.strip().split("\t")[0]
        sen = whole_sen.split(maxsplit=5)
        ori_sen = sen[5].strip()
        sentence = ori_sen.split(" ")
        entity_offset.append([int(sen[2]), int(sen[4])])
        parse_result = spacy_model(ori_sen)
        sub_graph = []
        sub_entity_concat = []
        token_concat = []
        graph = None
        for token in parse_result:
            token_concat.append('{0}-{1}'.format(token.lower_, token.i))
            # print('{0}-{1}'.format(token.lower_, token.i))
            for child in token.children:
                sub_graph.append(('{0}-{1}'.format(token.lower_, token.i),
                                  '{0}-{1}'.format(child.lower_, child.i)))
            if token.i in entity_offset[index]:
                sub_entity_concat.append('{0}-{1}'.format(token.lower_, token.i))
                assert token.lower_ == sentence[token.i].lower(), (sentence[token.i].lower(), token.lower_)
        edges.append(sub_graph)
        graph = nx.Graph(sub_graph)
        try:
            short_path = nx.shortest_path(graph, source=sub_entity_concat[0], target=sub_entity_concat[1])
            for word_concat in token_concat:
                if word_concat.split("-")[0].strip() in sim_feature_set:
                    # print(word_concat.split("-")[0].strip())
                    filter_num += 1
                    label[index_list[j]] = sponsor_label
                    # print(index_list[j])
                    break
        except:
            continue

    with open("temp/results_post_sponsor.txt", "w", encoding="utf-8") as fmodel:
        for i, item in enumerate(label):
            fmodel.write(item + "\t" + score[i] + "\n")
    return True


def generate_relation_cs(edl_cs_string):
    out_list = generate_cs_file(edl_cs_string, rel_map_ERE, ERE_to_AIDA_final_ouput)
    return out_list