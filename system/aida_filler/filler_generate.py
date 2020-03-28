import os
import json
import argparse
# import io
import codecs

def load_unit_gaz(units_path):
    gaz = set()
    with open(units_path) as f:
        lines = f.readlines()

    for line in lines:
        gaz.add(line.strip())
    return gaz

def single_generate(corenlp_dir, output_dir):
    ner_cache = set()
    for doc in os.listdir(corenlp_dir):
        index = 0
        f_out = open(os.path.join(output_dir, doc.replace('.rsd.txt.json','.cs')), 'w')
        with open(os.path.join(corenlp_dir,doc)) as f:
            content = f.read()
        json_f = json.loads(content)
        for sentence in json_f['sentences']:
            for entitymention in sentence['entitymentions']:
                ner = entitymention['ner']
                if ner not in ner_cache:
                    ner_cache.add(ner)
                characterOffsetBegin = str(entitymention['characterOffsetBegin'])
                characterOffsetEnd = str(entitymention['characterOffsetEnd']-1)
                text = entitymention['text']
                if ner != 'TIME' and ner != 'DATE':
                    continue
                if ner == 'DATE':

                    print(text, characterOffsetBegin, characterOffsetEnd)
                filler_id = ':Entity_Filler_ENG_%s'%(format(index, '07d'))
                filler_type = 'TME'
                filler_offset = doc_name+':'+'-'.join([characterOffsetBegin,characterOffsetEnd])
                confidence = 1.000
                f_out.write('%s\ttype\tTME\n'%filler_id)
                f_out.write('%s\t%s\t%s\t%s\t%s\n'%(filler_id, 'mention','"'+text+'"', filler_offset, confidence))
                index += 1
        f_out.close()



def whole_generate(corenlp_dir, text_dir, unit_gaz, edl_dict):
    filter_token_list = ['/','\\',':','{','}','[',']']
    filler_dict = {}
    ner_cache = set()
    token_dict = {}
    text_dict = {}
    filler_index = 0
    relation_dict = {}
    edl_filter_dict = {}
    for doc in os.listdir(corenlp_dir):
        doc_name = doc.replace(".rsd.txt.json", "")
        print(doc_name)
        article = ''
        if doc_name in edl_dict:
            edl_list = edl_dict[doc_name]
        else:
            edl_list = {}
        relation_dict[doc_name] = []
        edl_filter_dict[doc_name] = []
        text_path = os.path.join(text_dir, doc_name + '.rsd.txt')
        with open(text_path, encoding='utf-8') as f:
            article = f.read()
        text_dict[doc_name] = article

        with open(os.path.join(corenlp_dir,doc), encoding='utf-8') as f:
            content = f.read()
        if doc_name not in filler_dict:

            filler_dict[doc_name] = {}
            filler_dict[doc_name]['URL'] = []
            filler_dict[doc_name]['TME'] = []
            filler_dict[doc_name]['MON'] = []
            filler_dict[doc_name]['TTL'] = []
            filler_dict[doc_name]['VAL'] = []
        json_f = json.loads(content)
        
        for sentence in json_f['sentences']:
            token_list = []
            dependency_dict = {}
            for dependency in sentence['basicDependencies']:
                governor = dependency['governor']
                governorGloss = dependency['governorGloss']
                dependent = dependency['dependent']
                dependentGloss = dependency['dependentGloss']
                dep = dependency['dep']
                
                if dependent not in dependency_dict:
                    dependency_dict[dependent] = [governor, governorGloss, dependent, dependentGloss, dep]

                else:
                    print('error')
            
            for token in sentence['tokens']:
                token_list.append([token['originalText'], token['characterOffsetBegin'], token['characterOffsetEnd'], token['ner']])

            token_text_list = [x[0] for x in token_list]

            sentence_start = int(token_list[0][1])
            sentence_end = int(token_list[0][2])-1

            provenance = doc_name+':'+str(token_list[0][1])+'-'+str(token_list[-1][2]-1)
            for entitymention in sentence['entitymentions']:
                ner = entitymention['ner']
                if ner not in ner_cache:
                    ner_cache.add(ner)
                characterOffsetBegin = str(entitymention['characterOffsetBegin'])
                characterOffsetEnd = str(entitymention['characterOffsetEnd']-1)
                index_start = entitymention['tokenBegin']
                index_end = entitymention['tokenEnd']
                text = entitymention['text']

                #if ner != 'TIME' and ner != 'DATE':
                #    continue
                if ner == 'DATE':
                    try:
                        norm_text = entitymention['normalizedNER']
                    except:
                        norm_text = text
                    filler_dict[doc_name]['TME'].append([[text,norm_text], characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                elif ner == 'TIME':
                    try:
                        norm_text = entitymention['normalizedNER']
                    except:
                        norm_text = text

                    filler_dict[doc_name]['TME'].append([[text,norm_text], characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                    
                #elif ner == 'DURATION':
                #    if index_end <len(token_list):
                #        print([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]],doc)
                elif ner == 'URL':
                    filler_dict[doc_name]['URL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_id = ':Entity_Filler_ENG_%s'%(format(filler_index, '07d'))
                    filler_index += 1
                    if 'ORG' in edl_list:
                        for onename in edl_list['ORG']:
                            
                            if (int(onename.split('-')[0]) <= int(characterOffsetBegin) and int(characterOffsetBegin) <= int(onename.split('-')[1])) or (int(characterOffsetBegin)<=int(onename.split('-')[0]) and int(onename.split('-')[0]) <= int(characterOffsetEnd)):
                                edl_filter_dict[doc_name].append(onename)
                                relation_dict[doc_name].append([edl_list['ORG'][onename][-1], 'GeneralAffiliation.OrganizationWebsite', filler_id, provenance])
#                                print(' '.join(token_text_list))
#                                print('General-Affiliation.Organization-Website: %s\t%s\n'%(edl_list['ORG'][onename][0], text))
                                #print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GenAfl.OrgWeb\t%s\t1.0'%(edl_list['ORG'][onename][-1], filler_id ))
                            elif int(onename.split('-')[0]) >= sentence_start and int(onename.split('-')[1]) <= sentence_end:
#                                print(' '.join(token_text_list))
#                                print('General-Affiliation.Organization-Website: %s\t%s\n'%(edl_list['ORG'][onename][0], text))
                                relation_dict[doc_name].append([edl_list['ORG'][onename][-1], 'GeneralAffiliation.OrganizationWebsite', filler_id, provenance])
#                                print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GenAfl.OrgWeb\t%s\t1.0'%(edl_list['ORG'][onename][-1], filler_id ))
                elif ner == 'NUMBER':
                    flag_filter = False
                    for filter_token in filter_token_list:
                        if filter_token in text:
                            flag_filter = True
                            break
                    if flag_filter == True:
                        continue

                    #filler_dict[doc_name]['NUMBER'].append([text, characterOffsetBegin, characterOffsetEnd, filler_index])
                    
                    
                    filler_dict[doc_name]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_id = ':Entity_Filler_ENG_%s'%(format(filler_index, '07d'))
                    val_flag = False
                    if index_end <len(token_list):

                        
                        for ner_type in edl_list:
                            #if ner_type not in ['VEH','WEA']:
                            #    continue
                            for onename in edl_list[ner_type]:
                                
                                if (int(onename.split('-')[0]) - int(characterOffsetEnd)  <= 2) and (int(onename.split('-')[0]) -int(characterOffsetEnd) > 0):
                                    relation_dict[doc_name].append([filler_id, 'Measurement.Count', edl_list[ner_type][onename][-1], provenance])
#                                    print(' '.join(token_text_list))
#                                    print('Measurement.Count: %s\t%s\n'%(text, edl_list[ner_type][onename][0]))
                                    ######filler_dict[doc_name]['VAL'].append([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]])
                                    #print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Measurement.Count\t%s\t1.0'%(edl_list[ner_type][onename][-1], filler_id ))
                                    #print([text+' '+edl_list['VEH'][onename][0], characterOffsetBegin, token_list[index_end][2]])
                                    ###print(doc, ner_type, text, edl_list[ner_type][onename][0],'|||', article[int(characterOffsetBegin): int(onename.split('-')[1])+1])
                                                                            
                        for one_unit in unit_gaz:
                            if token_list[index_end][0].lower() == one_unit.lower():
                                #print(text,token_list[index_end][0], one_unit)
                                filler_dict[doc_name]['VAL'].append([text, characterOffsetBegin, token_list[index_end][2]-1, format(filler_index, '07d') ])
                                ######filler_dict[doc_name]['VAL'].append([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]])
                                val_flag = True
                                continue
                    if val_flag == False:
                        filler_dict[doc_name]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d') ])
                                                                            
                    filler_index += 1
                            
                elif ner == 'MONEY':
                    filler_dict[doc_name]['MON'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1

                elif ner == 'PERCENT':
                    #print(text, characterOffsetBegin, characterOffsetEnd)
                    filler_dict[doc_name]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                elif ner == 'TITLE':
                    filler_dict[doc_name]['TTL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1

    return filler_dict, edl_filter_dict, relation_dict

def read_edl(edl_path):
    edl_dict = {}
    edl_type_dict = {}

    # with open(edl_path, encoding='utf-8') as f:
    #     lines = f.readlines()
    # for line in lines:
    print(edl_path)
    # for line in io.open(edl_path, encoding='utf-8'):
    for line in codecs.open(edl_path, 'r', 'utf-8'):
        if len(line.strip().split('\t')) < 3:
            continue
        if line.strip().split('\t')[1] == 'type':
            edl_type_dict[line.strip().split('\t')[0]] = line.strip().split('\t')[2]
        elif 'mention' in line.strip().split('\t')[1]:
            if line.strip().split('\t')[3].split(':')[0] not in edl_dict:

                edl_dict[line.strip().split('\t')[3].split(':')[0]] = {}
            if edl_type_dict[line.strip().split('\t')[0]] not in edl_dict[line.strip().split('\t')[3].split(':')[0]]:
                edl_dict[line.strip().split('\t')[3].split(':')[0]][edl_type_dict[line.strip().split('\t')[0]]] = {}
            edl_dict[line.strip().split('\t')[3].split(':')[0]][edl_type_dict[line.strip().split('\t')[0]]][line.strip().split('\t')[3].split(':')[-1]] = [line.strip().split('\t')[2][1:-1], line.strip().split('\t')[3].split(':')[-1], edl_type_dict[line.strip().split('\t')[0]], line.strip().split('\t')[0]]

    return edl_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filler Extraction')
    parser.add_argument('--corenlp_dir', type=str, help='path of the directory of CoreNLP outputs')
    parser.add_argument('--edl_path', type=str, help = 'path of the edl CS file')
    parser.add_argument('--text_dir', type=str, help = 'path of the directory of rsd files')
    parser.add_argument('--units_path', default='units_clean.txt', help = 'file containing units')
    parser.add_argument('--filler_path', type=str, help = 'path of the generated filler CS file')
    parser.add_argument('--relation_path', type=str, help = 'path of the generated new relation CS file')
    args = parser.parse_args()

    edl_dict = read_edl(args.edl_path)
    unit_gaz = load_unit_gaz(args.units_path)
                                                                            

    filler_dict, edl_filter_dict, relation_dict = whole_generate(args.corenlp_dir, args.text_dir, unit_gaz, edl_dict)

    f_filler = open(args.filler_path,'w')

    for doc in filler_dict:
        for filler_type in filler_dict[doc]:
            for one_filler in filler_dict[doc][filler_type]:

                if filler_type == 'TME':
                    f_filler.write(':Entity_Filler_ENG_%s\ttype\t%s\n'%(one_filler[3], filler_type))
                    f_filler.write(':Entity_Filler_ENG_%s\tcanonical_mention\t%s\t%s\t1.0\n'%(one_filler[3], '"'+one_filler[0][0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
                    f_filler.write(':Entity_Filler_ENG_%s\tmention\t%s\t%s\t1.0\n'%(one_filler[3], '"'+one_filler[0][0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
                    f_filler.write(':Entity_Filler_ENG_%s\tnormalized_mention\t%s\t%s\t1.0\n'%(one_filler[3], '"'+one_filler[0][1]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
                else:
                    f_filler.write(':Entity_Filler_ENG_%s\ttype\t%s\n'%(one_filler[3], filler_type))
                    f_filler.write(':Entity_Filler_ENG_%s\tcanonical_mention\t%s\t%s\t1.0\n'%(one_filler[3], '"'+one_filler[0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
                    f_filler.write(':Entity_Filler_ENG_%s\tmention\t%s\t%s\t1.0\n'%(one_filler[3], '"'+one_filler[0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
    f_filler.close()


    f_relation = open(args.relation_path, 'w')
    for doc in relation_dict:
        for one_relation in relation_dict[doc]:

            f_relation.write('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#%s\t%s\t%s\t1.0\n'%(one_relation[0], one_relation[1], one_relation[2], one_relation[3]))
        
    f_relation.close()

