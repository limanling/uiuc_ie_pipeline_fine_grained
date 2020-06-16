import os
import xml.etree.ElementTree as ET
import json
import argparse

new_event_type = {
'vote':'Government.Vote',
'ballot':'Government.Vote',
'poll':'Government.Vote',
'referendum':'Government.Vote',
'election':'Government.Vote',
'referendum':'Government.Vote',
'voting':'Government.Vote',
'agreement':'Government.Agreements',
'spy':'Government.Spy.Spy',
'crash': 'Disaster.AccidentCrash.AccidentCrash',
# 'fall down': 'Movement.TransportPerson.Fall',
}

new_event_role = {
'Government.Vote':{'nsubj':'Voter', 'nmod:for':'Candidate', 'dobj':'Candidate','nmod:in':'Place'},
'Government.Spy.Spy':{'nsubj':'Spy', 'nmod:for':'Beneficiary', 'dobj':'ObservedEntity','nmod:in':'Place'},
'Disaster.AccidentCrash.AccidentCrash':{'compound':'CrashObject', 'nsubj':'CrashObject', 'nmod:in':'Place'},
'Government.Agreements':{'nmod':'Participant', 'compound':'Place', 'nsubj':'Participant', 'nmod:in':'Place'},
# 'Movement.TransportPerson.Fall': {'':'', '':''}
}


role_ner_dict = {
    'Voter':['PER'],
    'Candidate':['PER', 'ORG', 'LAW', 'SID'],
    'Place':['GPE', 'LOC', 'FAC'],
    'Spy':['PER'],
    'Beneficiary':['PER','ORG', 'GPE','SID'],
    'ObservedEntity':['ORG', 'GPE','SID'],
    'CrashObject':['COM', 'FAC', 'LOC', 'PER', 'VEH', 'WEA'],
    'Participant':['GPE', 'SID']
}

framenet_aida_map = {
'Conquering':'Transaction.Transfer-Control',
'Criminal_investigation':'Justice.Investigate',
'Sign_agreement':'Government.Agreements',
'Inspecting':'Inspection',
'Destroying':'Existence.Damage-Destroy',
'Damaging':'Existence.Damage-Destroy'
}

framenet_role_map = {
'Government.Vote':{'Voter':'Receiver','Candidate':'Territory','Place':'Place','Time':'Date'},
'Government.Spy':{'Investigator':'Investigator','Suspect':'Investigatee','Incident':'Crime','Time':'Date'}
}

prefix = "https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#"

def read_filler(filler_path):
    filler_dict = {}
    filler_type_dict = {}
    with open(filler_path) as f:
        lines = f.readlines()
    for line in lines:
        if len(line.strip().split('\t')) < 3:
            continue
        filler_id = line.strip().split('\t')[0]
        if line.strip().split('\t')[1] == 'type':
            filler_type_dict[line.strip().split('\t')[0]] = line.strip().split('\t')[2]
        if line.strip().split('\t')[1] == 'mention':
            if line.strip().split('\t')[3].split(':')[0] not in filler_dict:
                filler_dict[line.strip().split('\t')[3].split(':')[0]] = []
            filler_text = line.strip().split('\t')[2][1:-1]
            offset = line.strip().split('\t')[3].split(':')[1]
            filler_dict[line.strip().split('\t')[3].split(':')[0]].append([int(offset.split('-')[0]), int(offset.split('-')[1]), filler_id, filler_text])
#            print([int(offset.split('-')[0]), int(offset.split('-')[1]), filler_id, filler_text])
    return filler_type_dict, filler_dict
        
def read_edl(edl_path):
    edl_dict = {}
    edl_type_dict = {}
    with open(edl_path) as f:
        lines = f.readlines()
    for line in lines:
        if len(line.strip().split('\t')) < 3:
            continue
        edl_id = line.strip().split('\t')[0]
        if line.strip().split('\t')[1] == 'type':
            edl_type_dict[line.strip().split('\t')[0]] = line.strip().split('\t')[2]
        if 'mention' in line.strip().split('\t')[1]:
            if line.strip().split('\t')[3].split(':')[0] not in edl_dict:
                edl_dict[line.strip().split('\t')[3].split(':')[0]] = []
            edl_text = line.strip().split('\t')[2][1:-1]
            offset = line.strip().split('\t')[3].split(':')[1]
            edl_dict[line.strip().split('\t')[3].split(':')[0]].append([int(offset.split('-')[0]), int(offset.split('-')[1]), edl_id, edl_text])
#            print([int(offset.split('-')[0]), int(offset.split('-')[1]), edl_id, edl_text])
    return edl_type_dict,edl_dict

def read_event(event_path):

    with open(event_path) as f:
        lines = f.readlines()

    event_dict = {}
    for line in lines:

        if len(line.split('\t')) < 3:
            continue

        if 'mention' not in line.split('\t')[1]:
            continue
        doc_id = line.split('\t')[3].split(':')[0]
        offset = line.split('\t')[3].split(':')[1]
        event_id = line.split('\t')[0]
        trigger = line.split('\t')[2][1:-1]
        if doc_id not in event_dict:
            event_dict[doc_id] = []
        event_dict[doc_id].append([int(offset.split('-')[0]), int(offset.split('-')[1]), event_id, trigger])
    return event_dict

def agument_event(event_path, event_dict):
    with open(event_path) as f:
        lines = f.readlines()

    for line in lines:

        if len(line.split('\t')) < 3:
            continue

        if 'mention' not in line.split('\t')[1]:
            continue
        doc_id = line.split('\t')[3].split(':')[0]
        offset = line.split('\t')[3].split(':')[1]
        event_id = line.split('\t')[0]
        trigger = line.split('\t')[2][1:-1]
        if doc_id not in event_dict:
            event_dict[doc_id] = []
        event_dict[doc_id].append([int(offset.split('-')[0]), int(offset.split('-')[1]), event_id, trigger])
    return event_dict


head = '''
<!DOCTYPE html>
<html>
<head>
<title>Page Title</title>
</head>
<body>
'''

tail = '''
</body>
</html>
'''

parser_map = {'-RRB-': ')', '-LRB-': '(', '-RCB-': '}', '-LCB-': '{', '-RSB-': ']', '-LSB-': '[', '``':'"', "''":'"'}

def extract_rel_dependency(text_dir, corenlp_dir, edl_path, filler_path, event_path,
                           event_path_aug, new_event_path, visual_path):
    f_new_event = open(new_event_path,'w')

    filler_type_dict, filler_dict = read_filler(filler_path)
    edl_type_dict,edl_dict = read_edl(edl_path)

    frame_net_dict = {}

    new_event_dict = {}


    html_page = []

    # print(framenet_role_map)

    with open(event_path) as f:
        lines = f.readlines()

    event_dict = read_event(event_path)
    event_dict = agument_event(event_path_aug, event_dict)

    new_event_index = 0
    for doc_id in os.listdir(corenlp_dir):
        doc = doc_id.split('.')[0]
        new_event_dict[doc] = []

        with open(os.path.join(text_dir, doc+'.rsd.txt')) as f:
            content = f.read()

        if doc_id.split('.')[0] in event_dict:
            event_list = event_dict[doc_id.split('.')[0]]
        else:
            event_list = []

        with open(os.path.join(corenlp_dir, doc_id)) as f:
            core_text = f.read()

        json_core = json.loads(core_text)

        for sentence in json_core['sentences']:

            token_list = []
            dependency_dict = {}
            governer_dict = {}
            for dependency in sentence['enhancedDependencies']:
                governor = dependency['governor']
                governorGloss = dependency['governorGloss']
                dependent = dependency['dependent']
                dependentGloss = dependency['dependentGloss']
                dep = dependency['dep']

                if dependent not in dependency_dict:
                    dependency_dict[dependent] = []

                dependency_dict[dependent].append([governor, governorGloss, dependent, dependentGloss, dep])
                if governor not in governer_dict:
                    governer_dict[governor] = []
                governer_dict[governor].append([governor, governorGloss, dependent, dependentGloss, dep])

            for token in sentence['tokens']:
                characterOffsetBegin = token['characterOffsetBegin']
                characterOffsetEnd = token['characterOffsetEnd'] - 1
                token_list.append([token['originalText'], token['pos'], characterOffsetBegin, characterOffsetEnd])

            for index,token in enumerate(token_list):
                target_offset_start = token[2]
                target_offset_end = token[3]
                target_text = token[0]
                new_event_trigger = token[0]
                for xx in new_event_type:
                    event_type = new_event_type[xx]

                    if token[0].lower()[:len(xx)]!=xx:
                        continue

                    # if token[1][:2] != 'VB':
                    #     continue
                    if index+1 not in governer_dict:
                        continue



                    flag = False
                    for trigger in event_list:
                        if trigger[0] >=target_offset_start and trigger[0]<=target_offset_end or target_offset_start>=trigger[0] and target_offset_start<=trigger[1]:
                            #if trigger[3] == target_text:
                            flag = True
                            break
                    if flag == True:
                        continue

    #                print(target_text)

                    new_event_index += 1

                    new_arg_list = []
                    new_event_id = ':Event_new_type_plus_%s'%(format(new_event_index, '07d'))

                    new_event_offset = doc+':'+str(target_offset_start)+'-'+str(target_offset_end)
                    new_event_dict[doc].append([event_type, new_event_offset, new_event_trigger])
                    new_event_index += 1

                    new_arg_list = []
                    for dependent_relation in governer_dict[index+1]:

                        arg_candidate = token_list[dependent_relation[2]-1]


                        ele_offset_start = arg_candidate[2]
                        ele_offset_end = arg_candidate[3]
                        #event_role = framenet_aida_map[target_name]+'_'+framenet_role_map[target_name][element_name] + '.actual'
                        #event_role_offset = doc+':'+str(ele_offset_start)+'-'+str(ele_offset_end)
                        #event_role_mention = content[ele_offset_start: ele_offset_end + 1]

                        #for some event type, match with edl and filler:


                        if dependent_relation[4] == 'nmod:for':
                            if 'nmod:for' not in new_event_role[new_event_type[xx]]:
                                continue
                            new_arg_role_x = new_event_role[new_event_type[xx]]['nmod:for']
                            ner_type = role_ner_dict[new_arg_role_x]
    ###                        print(xx, token[1], dependent_relation, new_event_role[new_event_type[xx]]['nmod:for'])
                            for one_entity in edl_dict[doc]:
                                entity_start = one_entity[0]
                                entity_end = one_entity[1]
                                entity_type = edl_type_dict[one_entity[2]]
                                entity_text = one_entity[3]
                                if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:
                                    new_arg_role = event_type+'_'+new_arg_role_x+'.actual'
                                    if entity_type not in ner_type:
                                        continue
                                        ###                                print('%s\t%s\t%s\t%s\t%s'%('new_event_id', new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))
                                    if [new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                                        new_arg_list.append([new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
                                        html_page.append([[content[token_list[0][2]:token_list[-1][3]+1], token_list[0][2], token_list[-1][3]], [event_type, target_offset_start, target_offset_end, new_event_trigger], [new_arg_role, entity_start, entity_end, entity_text]   ])

                        if dependent_relation[4][:len('nsubj')] == 'nsubj':
                            if 'nsubj' not in new_event_role[new_event_type[xx]]:
                                continue
                            new_arg_role_x = new_event_role[new_event_type[xx]]['nsubj']
                            ner_type = role_ner_dict[new_arg_role_x]
    ###                        print(xx, token[1], dependent_relation, new_event_role[new_event_type[xx]]['nsubj'])
    ###                        print(' '.join([x[0] for x in token_list]))
                            if doc not in edl_dict:
                                continue
                            for one_entity in edl_dict[doc]:
                                entity_start = one_entity[0]
                                entity_end = one_entity[1]
                                entity_type = edl_type_dict[one_entity[2]]
                                entity_text = one_entity[3]
                                if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:
                                    new_arg_role = event_type+'_'+new_arg_role_x+'.actual'
                                    if entity_type not in ner_type:
                                        continue
                                        ###                                print('%s\t%s\t%s\t%s\t%s'%('new_event_id', new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))

                                    if [new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                                        new_arg_list.append([new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
                                        html_page.append([[content[token_list[0][2]:token_list[-1][3]+1], token_list[0][2], token_list[-1][3]], [event_type, target_offset_start, target_offset_end, new_event_trigger], [new_arg_role, entity_start, entity_end, entity_text]   ])

                        if dependent_relation[4] == 'nmod:in':
                            if 'nmod:in' not in new_event_role[new_event_type[xx]]:
                                continue
                            new_arg_role_x = new_event_role[new_event_type[xx]]['nmod:in']
                            ner_type = role_ner_dict[new_arg_role_x]

    ###                        print(xx, token[1], dependent_relation, new_event_role[new_event_type[xx]]['nmod:in'])
    ###                        print(' '.join([x[0] for x in token_list]))
                            for one_entity in edl_dict[doc]:
                                entity_start = one_entity[0]
                                entity_end = one_entity[1]
                                entity_type = edl_type_dict[one_entity[2]]
                                entity_text = one_entity[3]
                                if entity_type == 'TME':
                                    new_arg_role_x = 'Time'
                                else:
                                    new_arg_role_x = 'Place'
                                if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:
                                    new_arg_role = event_type+'_'+new_arg_role_x+'.actual'
                                    if entity_type not in ner_type:
                                        continue
                                    # print('%s\t%s\t%s\t%s\t%s'%('new_event_id', new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))
                                    if [new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                                        new_arg_list.append([new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
                                        html_page.append([[content[token_list[0][2]:token_list[-1][3]+1], token_list[0][2], token_list[-1][3]], [event_type, target_offset_start, target_offset_end, new_event_trigger], [new_arg_role, entity_start, entity_end, entity_text]   ])


                        if dependent_relation[4][:len('dobj')] == 'dobj':
                            if 'dobj' not in new_event_role[new_event_type[xx]]:
                                continue
                            new_arg_role_x = new_event_role[new_event_type[xx]]['dobj']
                            ner_type = role_ner_dict[new_arg_role_x]
    ###                        print(xx, token[1], dependent_relation, new_event_role[new_event_type[xx]]['dobj'])
    ###                        print(' '.join([x[0] for x in token_list]))
                            for one_entity in edl_dict[doc]:
                                entity_start = one_entity[0]
                                entity_end = one_entity[1]
                                entity_type = edl_type_dict[one_entity[2]]
                                entity_text = one_entity[3]


                                if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:
                                    new_arg_role = event_type+'_'+new_arg_role_x+'.actual'
                                    # print('aaaaaaa',new_arg_role)
                                    if entity_type not in ner_type:
                                        continue
                                        ###                                print('%s\t%s\t%s\t%s\t%s'%(new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))

                                    if [new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                                        new_arg_list.append([new_event_id, new_arg_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
                                        html_page.append([[content[token_list[0][2]:token_list[-1][3]+1], token_list[0][2], token_list[-1][3]], [event_type, target_offset_start, target_offset_end, new_event_trigger], [new_arg_role, entity_start, entity_end, entity_text]   ])

                    f_new_event.write('%s\t%s\t%s%s\n'%(new_event_id,'type',prefix,event_type))
                    f_new_event.write('%s\t%s\t"%s"\t%s\t%s\n'%(new_event_id, 'mention.actual', new_event_trigger, new_event_offset, '1.0'))
                    f_new_event.write('%s\t%s\t"%s"\t%s\t%s\n'%(new_event_id, 'canonical_mention.actual', new_event_trigger, new_event_offset, '1.0'))
                    # print('%s\t%s\t%s%s'%(new_event_id,'type',prefix,event_type))
                    # print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'mention.actual', new_event_trigger, new_event_offset, '1.0'))
                    # print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'canonical_mention.actual', new_event_trigger, new_event_offset, '1.0'))
                    for arg in new_arg_list:
                        f_new_event.write('%s\t%s%s\t%s\t%s\t%s\n'%(arg[0],prefix,arg[1],arg[2],arg[3],arg[4]))
                        # print('%s\t%s%s\t%s\t%s\t%s'%(arg[0],prefix,arg[1],arg[2],arg[3],arg[4]))

    f_new_event.flush()
    f_new_event.close()

    if visual_path:
        f_html = open(visual_path, 'w')
        f_html.write('%s\n'%head)
        count = 0
        for line in html_page:
            sentence = line[0]
            s_t = sentence[0]
            s_s = int(sentence[1])
            s_e= int(sentence[2])

            trigger = line[1]
            t_s = int(trigger[1])
            t_e = int(trigger[2])
            t_t = trigger[0]

            argument = line[2]
            a_r = argument[0]
            a_s= int(argument[1])
            a_e = int(argument[2])

            count = count+1
            f_html.write('<p>%d. Event type: %s;<br> Trigger: %s;<br> Argument: %s; Argument Role: %s </p>'%(count, trigger[0], trigger[3], argument[3], argument[0]))
            sent_out = []
            for index,char in enumerate(s_t):
                out_c = char
                if s_s + index ==t_s:
                    out_c = '<span style="color:blue">' + out_c
                if s_s + index == t_e:
                    out_c = out_c + '</span>'

                if s_s + index == a_s:
                    out_c = '<span style="color:orange">' + out_c
                if s_s + index == a_e:
                    out_c = out_c + '</span>'
                sent_out.append(out_c)
            f_html.write('<p>%s</p><br><br>'%(''.join(sent_out)))
        f_html.write('%s\n'%tail)
        f_html.close()

if __name__ == '__main__':
    # # ltf_dir = '/nas/data/m1/AIDA_Data/aida2018/evaluation/source/ltf'
    # ltf_dir = '/nas/data/m1/lim22/aida2019/dryrun/source/en'
    # # text_dir = '/nas/data/m1/AIDA_Data/aida2018/evaluation/source/rsd'
    # text_dir = '/nas/data/m1/lim22/aida2019/dryrun/source/en_rsd'
    # # corenlp_dir = '/nas/data/m1/lud2/AIDA/pilot/pilot/corenlp_exp'
    # corenlp_dir = '/nas/data/m1/lim22/aida2019/dryrun/source/en_corenlp'
    #
    # # edl_path = '/nas/data/m1/panx2/tmp/aida/eval/2018/en/0918/en.linking.corf.cs'
    # edl_path = '/nas/data/m1/lim22/aida2019/dryrun/0322/en/edl/merged.cs'
    # # filler_path = '/nas/data/m1/lud2/AIDA/pilot/results/filler/version5.1/filler_en.cs'
    # filler_path = '/nas/data/m1/lud2/AIDA/dryrun/201905/filler/en/filler_en_cleaned.cs'
    #
    # # dir_name = '0928_P103_Q004_H001_1hop'
    # # event_path = '/nas/data/m1/AIDA_Data/aida2018/evaluation/0922_R1/en/en_events_time_ex.cs'
    # event_path = '/nas/data/m1/lim22/aida2019/dryrun/0322/en/event/events_fine.cs'
    #
    # # event_path_aug = '/nas/data/m1/lud2/AIDA/pilot/results/new_event/%s/new_event_bi.cs'%dir_name
    # # new_event_path = '/nas/data/m1/lud2/AIDA/pilot/results/new_event/%s/new_event_plus_bi.cs'%dir_name
    # # visual_path = '/nas/data/m1/lud2/AIDA/pilot/results/new_event/%s/visualization_2rd_bi.html'%dir_name
    # event_path_aug = '/nas/data/m1/lim22/aida2019/dryrun/0322/en/event/events_fine_framenet.cs'
    # new_event_path = '/nas/data/m1/lim22/aida2019/dryrun/0322/en/event/events_fine_depen.cs'
    # visual_path = '/nas/data/m1/lim22/aida2019/dryrun/0322/en/event/events_fine_depen.html'

    parser = argparse.ArgumentParser()
    parser.add_argument('rsd_dir', type=str, help='rsd_dir')
    parser.add_argument('corenlp_dir', type=str, help='corenlp_dir')
    parser.add_argument('edl_path', type=str, help='edl_path')
    parser.add_argument('filler_path', type=str, help='filler_path')
    parser.add_argument('event_path', type=str, help='event_path')
    parser.add_argument('event_path_aug', type=str, help='event_path_aug')
    parser.add_argument('new_event_path', type=str, help='new_event_path')
    parser.add_argument('--visual_path', type=str, help='visual_path')

    args = parser.parse_args()

    text_dir = args.rsd_dir
    corenlp_dir = args.corenlp_dir
    edl_path = args.edl_path
    filler_path = args.filler_path
    event_path = args.event_path
    event_path_aug = args.event_path_aug
    new_event_path = args.new_event_path
    visual_path =args.visual_path

    extract_rel_dependency(text_dir, corenlp_dir, edl_path, filler_path, event_path,
                           event_path_aug, new_event_path, visual_path)

    print("Dependency based rules done. ")