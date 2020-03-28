import os
import xml.etree.ElementTree as ET
import json

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



ltf_dir = '/data/m1/zhangt13/aida2018/1118/E52/source/en'
frame_dir = '/data/m1/lud2/AIDA/data/1118/E52/en-sents-semafor'
text_dir = '/data/m1/zhangt13/aida2018/1118/E52/source/en_rsd'



edl_path = '/nas/data/m1/panx2/tmp/date/2018/1129/2018e52/en.linking.corf.cs'
filler_path = '/data/m1/lud2/AIDA/data/1118/E52/filler_en_cleaned.cs'

#dir_name = '0928_P103_Q002_H001_1hop'
event_path = '/data/m1/zhangt13/aida2018/1118/E52/event/en_event_time_ex.cs'
new_event_path = '/data/m1/lud2/AIDA/data/1118/E52/event/new_event.cs'#%dir_name
visual_path = '/data/m1/lud2/AIDA/data/1118/E52/event/visualization.html'#%dir_name
#os.mkdir('/data/m1/lud2/AIDA/pilot/results/new_event/%s'%dir_name)


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


f_new_event = open(new_event_path,'w')



parser_map = {'-RRB-': ')', '-LRB-': '(', '-RCB-': '}', '-LCB-': '{', '-RSB-': ']', '-LSB-': '[', '``':'"', "''":'"'}

filler_type_dict, filler_dict = read_filler(filler_path)
edl_type_dict,edl_dict = read_edl(edl_path)

frame_net_dict = {}

new_event_dict = {}
framenet_aida_map = {
'Conquering':'Transaction.TransferControl',
'Criminal_investigation':'Justice.Investigate',
'Sign_agreement':'Government.Agreements',
'Inspecting':'Inspection',
'Destroying':'Existence.DamageDestroy',
'Damaging':'Existence.DamageDestroy'
}

framenet_role_map = {
'Conquering':{'Conqueror':'Recipient','Theme':'Territory','Place':'Place','Time':'Time'},
'Criminal_investigation':{'Investigator':'Investigator','Suspect':'Investigatee','Incident':'Crime','Time':'Time'},
'Sign_agreement':{'Signatory':'Signer','Place':'Place','Time':'Time'},
'Inspecting':{'Inspector':'Inspector','Ground':'Person_Thing','Time':'Time'},
'Damaging':{'Agent':'Agent','Patient':'Victim','Instrument':'Instrument','Place':'Place','Time':'Time'},
'Destroying':{'Destroyer':'Agent','Patient':'Victim','Instrument':'Instrument','Place':'Place','Time':'Time'}

}

role_ner_dict = {
    'Recipient':['PER','ORG', 'GPE','SID'],
    'Territory':['GPE', 'LOC', 'FAC'],
    'Place':['GPE', 'LOC', 'FAC'],
    'Time':['TME'],
    'Investigator':['PER','ORG', 'GPE','SID'],
    'Investigatee':['PER','ORG', 'GPE','SID'],
    'Crime':['CRM'],
    'Signer':['GPE','SID'],
    'Inspector':['PER','ORG', 'GPE','SID'],
    'Person_Thing': ['PER','COM', 'VEH', 'WEA', 'FAC', 'BAL'],
    'Agent':['PER','ORG', 'GPE','SID'],
    'Victim':['COM', 'VEH', 'WEA', 'FAC', 'BAL'],
    'Instrument':['WEA', 'VEH', 'COM']
    
}


html_page = []

print(framenet_role_map)

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
    print('doc_id', doc_id, 'offset', offset, 'event_id', event_id, 'trigger', trigger)
    if doc_id not in event_dict:
        event_dict[doc_id] = []
    
    event_dict[doc_id].append([int(offset.split('-')[0]), int(offset.split('-')[1]), event_id, trigger])
    


new_event_index = 0
for doc in os.listdir(frame_dir):
    new_event_dict[doc] = []

    ltf_doc_id = doc + '.ltf.xml'
    print(ltf_dir, ltf_doc_id)
    with open(os.path.join(ltf_dir, ltf_doc_id)) as f:
        content = f.read()

    root = ET.fromstring(content)

    seg_list = []
    for seg in root[0][0].findall('SEG'):
        seg_list.append([seg.attrib['start_char'], seg.attrib['end_char'], seg.find('ORIGINAL_TEXT').text])

    with open(os.path.join(text_dir, doc+'.rsd.txt')) as f:
        content = f.read()

    with open(os.path.join(frame_dir, doc)) as f:
        lines = f.readlines()
    if len(lines) != len(seg_list):
        print(doc,'sss')
        continue



    if doc not in frame_net_dict:
        frame_net_dict[doc] = []

    if doc not in edl_dict:
        edl_dict[doc] = []
    if doc not in filler_dict:
        filler_dict[doc] = []

    for index,line in enumerate(lines):
        
        sentence_start = seg_list[index][0]
        sentence_end = seg_list[index][1]
        sentence_text = seg_list[index][2]
        event_list = []
        if doc in event_dict:
            tmp_dict = event_dict[doc]
        else:
            tmp_dict = {}
        for x in tmp_dict:
            if int(sentence_start)<=int(x[0]) and int(sentence_end)>=int(x[1]):
                event_list.append(x)
            

        #match with event trigger
        


        line_json = json.loads(line.strip())
        frame_net_dict[doc].append(line_json)
        token_list = []
        cha_start_index = 0
        for token in line_json['tokens']:
            if token in parser_map:
                token = parser_map[token]
            token_s_i = sentence_text.find(token, cha_start_index)
            
            token_e_i = token_s_i + len(token) -1

            if token_s_i == -1:
                offset_s = cha_start_index
                offset_e = cha_start_index + len(token) + 2
            else:
                offset_s = token_s_i
                offset_e = token_e_i
            if token_s_i!=-1 and content[int(sentence_start) + token_s_i: int(sentence_start) + token_e_i +1] != token:
                print(doc, content[int(sentence_start) + token_s_i: int(sentence_start) + token_e_i +1], token)

            if token_s_i!=-1:
                cha_start_index = token_e_i + 1 
            
#            print(token_s_i, token_e_i, token)
            token_list.append([token, int(sentence_start) + offset_s, int(sentence_start) + offset_e])
            
        for frame in line_json['frames']:
            target = frame['target']
            target_name = target['name']
            target_span = target['spans']
            target_start = target_span[0]['start']
            target_end = target_span[0]['end']
            target_text = target_span[0]['text']

            target_offset_start = token_list[int(target_start)][1]
            target_offset_end = token_list[int(target_end) -1][2]

            if target_offset_start == -1:
                print(target_name, target_text, target_offset_start, target_offset_end)
            if target_name not in framenet_aida_map:
                continue


            flag = False
            for trigger in event_list:
                if trigger[0] >=target_offset_start and trigger[0]<=target_offset_end or target_offset_start>=trigger[0] and target_offset_start<=trigger[1]:
###                    print(trigger[3], target_text)
#                if trigger[3] == target_text:
                    flag = True
                    break
            if flag == True:
                continue
            
            new_event_type = framenet_aida_map[target_name]
            new_event_offset = doc+':'+str(target_offset_start)+'-'+str(target_offset_end)
            new_event_trigger = content[target_offset_start: target_offset_end + 1]
            new_event_dict[doc].append([new_event_type, new_event_offset, new_event_trigger])
            
            new_event_id = ':Event_new_type_%s'%(format(new_event_index, '07d'))
            new_event_index += 1

            new_arg_list = []
###            print('%s\t%s\t%s'%(new_event_id,'type',new_event_type))
###            print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'mention.actual', new_event_trigger, new_event_offset, '1.0'))
###            print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'canonical_mention.actual', new_event_trigger, new_event_offset, '1.0'))


######            print(new_event_type, new_event_offset, new_event_trigger)
            element_cache = []
            annotationSets = frame['annotationSets']
            if len(annotationSets) > 1:
                print('annot sets', annotationSets)
            for one_element in annotationSets[0]['frameElements']:
                new_event_type_x = new_event_type
                element_name = one_element['name']
                element_span = one_element['spans']
                element_start = element_span[0]['start']
                element_end = element_span[0]['end']
                element_text = element_span[0]['text']

 
                if element_name not in framenet_role_map[target_name]:
                    continue
                    
                ele_offset_start = token_list[int(element_start)][1]
                ele_offset_end = token_list[int(element_end) -1][2]
                event_role = framenet_aida_map[target_name]+'_'+framenet_role_map[target_name][element_name] + '.actual'
                event_role_offset = doc+':'+str(ele_offset_start)+'-'+str(ele_offset_end)
                event_role_mention = content[ele_offset_start: ele_offset_end + 1]
                ner_type = role_ner_dict[framenet_role_map[target_name][element_name]]
                
                
                #for some event type, match with edl and filler:
                for one_entity in edl_dict[doc]:
                    new_event_type_x = new_event_type
                    entity_start = one_entity[0]
                    entity_end = one_entity[1]
                    entity_type = edl_type_dict[one_entity[2]]
                    entity_text = one_entity[3]
                    if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:

                        if entity_type not in ner_type:
                            continue


                        if new_event_type=='Inspection':
                            if entity_type == 'PER':
                                new_event_type_x = 'Inspection.People'
                                event_role = new_event_type_x+'_'+'Person' + '.actual'
                                #print('frame',event_role_mention, 'edl',entity_text)
                            else:
                                new_event_type_x = 'Inspection.Artifact'
                                event_role = new_event_type_x+'_'+'Thing' + '.actual'

                        html_page.append([[content[int(sentence_start):int(sentence_end)+1], int(sentence_start), int(sentence_end)], [new_event_type_x, target_offset_start, target_offset_end, new_event_trigger], [event_role, entity_start, entity_end, entity_text]   ])
                        if event_role == 'Inspection_Person_Thing.actual':
                            print(new_event_type, entity_type, new_event_type)
                            print('####################%s\t%s\t%s\t%s\t%s'%(new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))
                        if [new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                            new_arg_list.append([new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
#                        print('%s\t%s\t%s\t%s\t%s'%(new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))
                              



                for one_entity in filler_dict[doc]:
                    new_event_type_x = new_event_type
                    entity_start = one_entity[0]
                    entity_end = one_entity[1]
                    entity_type = filler_type_dict[one_entity[2]]
                    entity_text = one_entity[3]
                    if ele_offset_start>=entity_start and ele_offset_start<=entity_end or entity_start>=ele_offset_start and entity_start<=ele_offset_end:

                        if entity_type not in ner_type:
                            continue
                        if new_event_type=='Inspection':
                            if entity_type != 'PER':
                                new_event_type_x = 'Inspection.Artifact'
                                event_role = new_event_type_x+'_'+'Thing' + '.actual'
                            else:
                                new_event_type_x = 'Inspection.People'
                                event_role = new_event_type_x+'_'+'Person' + '.actual'

                        html_page.append([[content[int(sentence_start):int(sentence_end)+1], sentence_start, sentence_end], [new_event_type_x, target_offset_start, target_offset_end, new_event_trigger], [event_role, entity_start, entity_end, entity_text]   ])
                        if [new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'] not in new_arg_list:
                            new_arg_list.append([new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'])
###                        print('%s\t%s\t%s\t%s\t%s'%(new_event_id, event_role, one_entity[2], doc+':'+str(entity_start)+'-'+str(entity_end), '1.0'))



                #for some event type, generate new filler

 



######                print(event_role,event_role_offset, ner_type, event_role_mention, element_text)
#                if content[ele_offset_start:ele_offset_end+1].strip() != element_text.strip():
#                    print('sss',element_text, 'ppp',content[ele_offset_start:ele_offset_end+1])



                element_cache.append([element_name, element_text])
                
            if new_event_type=='Inspection':
                continue
            f_new_event.write('%s\t%s\t%s\n'%(new_event_id,'type',new_event_type))
            f_new_event.write('%s\t%s\t"%s"\t%s\t%s\n'%(new_event_id, 'mention.actual', new_event_trigger, new_event_offset, '1.0'))
            f_new_event.write('%s\t%s\t"%s"\t%s\t%s\n'%(new_event_id, 'canonical_mention.actual', new_event_trigger, new_event_offset, '1.0'))
###            print('%s\t%s\t%s'%(new_event_id,'type',new_event_type))
###            print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'mention.actual', new_event_trigger, new_event_offset, '1.0'))
###            print('%s\t%s\t"%s"\t%s\t%s'%(new_event_id, 'canonical_mention.actual', new_event_trigger, new_event_offset, '1.0'))
            for arg in new_arg_list:
                f_new_event.write('%s\t%s\t%s\t%s\t%s\n'%(arg[0],arg[1],arg[2],arg[3],arg[4]))
###                print('%s\t%s\t%s\t%s\t%s'%(arg[0],arg[1],arg[2],arg[3],arg[4]))
##            print(framenet_aida_map[target_name], target_name, target_text, element_cache)
        #for x in line_json:
        #    print(x)
    


f_new_event.close()

f_html = open(visual_path, 'w')
f_html.write('%s\n'%head)
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
    
###    print('Trigger: %s'%trigger[3], 'Argument: %s'%argument[3])
    f_html.write('<p>Event type: %s; Trigger: %s; Argument: %s; Argument Role: %s </p>'%(trigger[0], trigger[3], argument[3], argument[0]))
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
