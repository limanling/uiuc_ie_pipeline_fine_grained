import os
import json
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
                filler_id = ':Filler_ENG_%s'%(format(index, '07d'))
                filler_type = 'TME'
                filler_offset = doc.split('.')[0]+':'+'-'.join([characterOffsetBegin,characterOffsetEnd])
                confidence = 1.000
                f_out.write('%s\ttype\tTME\n'%filler_id)
                f_out.write('%s\t%s\t%s\t%s\t%s\n'%(filler_id, 'mention','"'+text+'"', filler_offset, confidence))
                index += 1
        f_out.close()



def whole_generate(corenlp_dir, text_dir, unit_gaz, edl_dict):
    filler_dict = {}
    ner_cache = set()
    token_dict = {}
    text_dict = {}
    filler_index = 0
    relation_dict = {}
    edl_filter_dict = {}
    for doc in os.listdir(corenlp_dir):

        article = ''
        if doc.split('.')[0] in edl_dict:
            edl_list = edl_dict[doc.split('.')[0]]
        else:
            edl_list = {}
        relation_dict[doc.split('.')[0]] = []
        edl_filter_dict[doc.split('.')[0]] = []
        text_path = os.path.join(text_dir, doc.split('.')[0] + '.rsd.txt')
        with open(text_path) as f:
            article = f.read()
        text_dict[doc.split('.')[0]] = article

        with open(os.path.join(corenlp_dir,doc)) as f:
            content = f.read()
        if doc.split('.')[0] not in filler_dict:

            filler_dict[doc.split('.')[0]] = {}
            filler_dict[doc.split('.')[0]]['URL'] = []
            filler_dict[doc.split('.')[0]]['TME'] = []
            filler_dict[doc.split('.')[0]]['MON'] = []
            filler_dict[doc.split('.')[0]]['TTL'] = []
            filler_dict[doc.split('.')[0]]['VAL'] = []
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
            sentence_start = int(token_list[0][1])
            sentence_end = int(token_list[0][2])-1

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
                    filler_dict[doc.split('.')[0]]['TME'].append([[text,norm_text], characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                elif ner == 'TIME':
                    try:
                        norm_text = entitymention['normalizedNER']
                    except:
                        norm_text = text

                    filler_dict[doc.split('.')[0]]['TME'].append([[text,norm_text], characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                    
                #elif ner == 'DURATION':
                #    if index_end <len(token_list):
                #        print([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]],doc)
                elif ner == 'URL':
                    filler_dict[doc.split('.')[0]]['URL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_id = ':Filler_ENG_%s'%(format(filler_index, '07d'))
                    filler_index += 1
                    if 'ORG' in edl_list:
                        for onename in edl_list['ORG']:
                            
                            if (int(onename.split('-')[0]) <= int(characterOffsetBegin) and int(characterOffsetBegin) <= int(onename.split('-')[1])) or (int(characterOffsetBegin)<=int(onename.split('-')[0]) and int(onename.split('-')[0]) <= int(characterOffsetEnd)):
                                edl_filter_dict[doc.split('.')[0]].append(onename)
                                relation_dict[doc.split('.')[0]].append([edl_list['ORG'][onename][-1], 'General-Affiliation.Organization-Website', filler_id])
                                #print(doc, text, edl_list['ORG'][onename][0])
                                #print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GenAfl.OrgWeb\t%s\t1.0'%(edl_list['ORG'][onename][-1], filler_id ))
                            elif int(onename.split('-')[0]) >= sentence_start and int(onename.split('-')[1]) <= sentence_end:
                                #print(doc, text, edl_list['ORG'][onename][0])
                                relation_dict[doc.split('.')[0]].append([edl_list['ORG'][onename][-1], 'General-Affiliation.Organization-Website', filler_id])
#                                print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#GenAfl.OrgWeb\t%s\t1.0'%(edl_list['ORG'][onename][-1], filler_id ))
                elif ner == 'NUMBER':
                    #filler_dict[doc.split('.')[0]]['NUMBER'].append([text, characterOffsetBegin, characterOffsetEnd, filler_index])
                    filler_dict[doc.split('.')[0]]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_id = ':Filler_ENG_%s'%(format(filler_index, '07d'))
                    val_flag = False
                    if index_end <len(token_list):

                        
                        for ner_type in edl_list:
                            #if ner_type not in ['VEH','WEA']:
                            #    continue
                            for onename in edl_list[ner_type]:
                                
                                if (int(onename.split('-')[0]) - int(characterOffsetEnd)  <= 2) and (int(onename.split('-')[0]) -int(characterOffsetEnd) > 0):
                                    relation_dict[doc.split('.')[0]].append([filler_id, 'Measurement.Count', edl_list[ner_type][onename][-1]])
                                                                            
                                    ######filler_dict[doc.split('.')[0]]['VAL'].append([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]])
                                    #print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#Measurement.Count\t%s\t1.0'%(edl_list[ner_type][onename][-1], filler_id ))
                                    #print([text+' '+edl_list['VEH'][onename][0], characterOffsetBegin, token_list[index_end][2]])
                                    ###print(doc, ner_type, text, edl_list[ner_type][onename][0],'|||', article[int(characterOffsetBegin): int(onename.split('-')[1])+1])
                                                                            
                        for one_unit in unit_gaz:
                            if token_list[index_end][0].lower() == one_unit.lower():
                                #print(text,token_list[index_end][0], one_unit)
                                filler_dict[doc.split('.')[0]]['VAL'].append([text, characterOffsetBegin, token_list[index_end][2]-1, format(filler_index, '07d') ])
                                ######filler_dict[doc.split('.')[0]]['VAL'].append([text+' '+token_list[index_end][0], characterOffsetBegin, token_list[index_end][2]])
                                val_flag = True
                                continue
                    if val_flag == False:
                        filler_dict[doc.split('.')[0]]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d') ])
                                                                            
                    filler_index += 1
#                        elif 'WEA' in edl_list:
#                            for onename in edl_list['WEA']:
#                                if (int(onename.split('-')[0]) - int(characterOffsetEnd)  <= 2) and (int(onename.split('-')[0]) -int(characterOffsetEnd) > 0):
#                                    #print([text+' '+edl_list['WEA'][onename][0], characterOffsetBegin, token_list[index_end][2]])
#                                    print(doc, 'wea', text, edl_list['WEA'][onename][0], '|||', article[int(characterOffsetBegin): int(onename.split('-')[1])])
                            
                elif ner == 'MONEY':
                    filler_dict[doc.split('.')[0]]['MON'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                #elif ner == 'ORDINAL':
                #    
                #    
                #    filler_dict[doc.split('.')[0]]['ORDINAL'].append([text, characterOffsetBegin, characterOffsetEnd, filler_index])
                #    filler_index += 1
                elif ner == 'PERCENT':
                    #print(text, characterOffsetBegin, characterOffsetEnd)
                    filler_dict[doc.split('.')[0]]['VAL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
                elif ner == 'TITLE':
                    filler_dict[doc.split('.')[0]]['TTL'].append([text, characterOffsetBegin, characterOffsetEnd, format(filler_index, '07d')])
                    filler_index += 1
#                    print([text, characterOffsetBegin, characterOffsetEnd])
    return filler_dict, edl_filter_dict, relation_dict

def read_edl(edl_path):
    edl_dict = {}
    edl_type_dict = {}

    
    with open(edl_path) as f:
        lines = f.readlines()
    for line in lines:
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
            #edl_dict[line.strip().split('\t')[3].split(':')[0]][line.strip().split('\t')[3].split(':')[-1]] = [line.strip().split('\t')[2][1:-1], line.strip().split('\t')[3].split(':')[-1], edl_type_dict[line.strip().split('\t')[0]]] 
    return edl_dict

corenlp_dir = '/nas/data/m1/lud2/AIDA/pilot/pilot/corenlp_asr'
edl_path = '/nas/data/m1/panx2/tmp/aida/eval/2018/en/0912_asr/en.linking.corf.cs'
text_dir = '/data/m1/AIDA_Data/aida2018/evaluation/source/en_asr_rsd/'
units_path = 'units_clean.txt'
f_filler = open('/data/m1/lud2/AIDA/pilot/results/filler/asr/filler_en.cs','w')
#output_path = '/data/m1/lud2/AIDA/pilot/results/en/timex/pilot_timex_en.cs'
#output_dir = '/data/m1/lud2/AIDA/pilot/results/en/timex/seperate/'

edl_dict = read_edl(edl_path)
unit_gaz = load_unit_gaz(units_path)
                                                                            

filler_dict, edl_filter_dict, relation_dict = whole_generate(corenlp_dir, text_dir, unit_gaz, edl_dict)


for doc in filler_dict:
    for filler_type in filler_dict[doc]:
        for one_filler in filler_dict[doc][filler_type]:
            #f_filler.write(':Filler_ENG_%s\ttype\t%s\n'%(one_filler[3], filler_type))
            #f_filler.write(':Filler_ENG_%s\tmention\t%s\t%s\n'%(one_filler[3], '"'+one_filler[0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
            #print(':Filler_ENG_%s\ttype\t%s'%(one_filler[3], filler_type))
            #print(':Filler_ENG_%s\tmention\t%s\t%s'%(one_filler[3], '"'+one_filler[0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
            if filler_type == 'TME':
                f_filler.write(':Filler_ENG_%s\ttype\t%s\n'%(one_filler[3], filler_type))
                f_filler.write(':Filler_ENG_%s\tmention\t%s\t%s\n'%(one_filler[3], '"'+one_filler[0][0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
                f_filler.write(':Filler_ENG_%s\tnormalized_mention\t%s\t%s\n'%(one_filler[3], '"'+one_filler[0][1]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
            else:
                f_filler.write(':Filler_ENG_%s\ttype\t%s\n'%(one_filler[3], filler_type))
                f_filler.write(':Filler_ENG_%s\tmention\t%s\t%s\n'%(one_filler[3], '"'+one_filler[0]+'"', doc+':'+str(one_filler[1])+'-'+str(one_filler[2])))
f_filler.close()



f_relation = open('/data/m1/lud2/AIDA/pilot/results/new_relation/asr/new_relation_en.cs','w')
for doc in relation_dict:
    for one_relation in relation_dict[doc]:
        f_relation.write('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#%s\t%s\t1.0\n'%(one_relation[0], one_relation[1], one_relation[2]))
        #print('%s\thttps://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#%s\t%s\t1.0'%(one_relation[0], one_relation[1], one_relation[2]))
f_relation.close()
#single_generate(corenlp_dir, output_dir)
