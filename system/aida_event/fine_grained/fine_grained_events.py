import ujson as json
import os
from collections import defaultdict, Counter
import argparse

from util.ltf_util import LTF_util
from util.finegrain_util import FineGrainedUtil

from nltk.stem.snowball import SnowballStemmer
from nltk import WordNetLemmatizer

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

event_newtype = {}
type_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
trigger_dict = defaultdict(lambda: defaultdict(str))
context_dict = defaultdict(lambda: defaultdict(str))

def stem_long(trigger, stemmer, lang):
    if lang.startswith('uk'):
        toks = []
        for trigger_sub in trigger.split(' '):
            if trigger_sub in stemmer:
                toks.append(stemmer[trigger_sub])
            else:
                toks.append(trigger_sub)
        return ' '.join(toks)
    else:
        return ' '.join([stemmer.stem(trigger_sub) for trigger_sub in trigger.split(' ')])

def load_stemmer(lang):
    if lang.startswith('en'):
        stemmer = SnowballStemmer("english")
        return stemmer
    elif lang.startswith('ru'):
        stemmer = SnowballStemmer("russian")
        return stemmer
    elif lang.startswith('uk'):
        stemmer = dict()
        for line in open('/nas/data/m1/lim22/aida/conf/lemmatization-uk.txt'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 2:
                stemmer[tabs[0]] = tabs[1]
    return stemmer

def load_mapping(mapping_file):
    mapping = {}
    for line in open(mapping_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        mapping[tabs[0]] = tabs[1]
    return mapping

# default mapping
newtype_mapping_backup = load_mapping(os.path.join(CURRENT_DIR, 'rules/mapping_backup.txt'))
# if here, directly mapping
newtype_mapping_sure = load_mapping(os.path.join(CURRENT_DIR, 'rules/mapping.txt'))

# if delete_type, directly delete
delete_type_sure = ['Business.DeclareBankruptcy', 'Business.End', 'Life.BeBorn', 'Life.Marry', 'Life.Divorce']
# after apply rules, delete if no result
delete_type_notsure = ['Business.Start', 'Business.Merge']

def load_arg_mapping(mapping_arg_file):
    mapping = defaultdict(lambda: defaultdict(str))
    for line in open(mapping_arg_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        if len(tabs) == 3:
            # newtype -> original role -> new role
            mapping[tabs[0]][tabs[1]] = tabs[2]
        else:
            print(line)
    return mapping

arg_mapping = load_arg_mapping(os.path.join(CURRENT_DIR, 'rules/mapping_args.txt'))

prefix = "https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#"

def prep_type_old(typestr):
    return typestr.replace("https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#", "")

def prep_arg_type_old(typestr):
    typestr = typestr.replace("https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#", "")\
        .replace(".actual", "")
    return typestr[typestr.find('_')+1:]

# read entity fingrain
def entity_finegrain_by_cs(entity_finegrain, entity_dict):
    # entity_dict = defaultdict(set)
    for line in open(entity_finegrain):
        if line.startswith(':Entity'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if tabs[1] == 'type':
                type_str = tabs[2].split('#')[-1]
                # add parent type
                tabs = type_str.split('.')
                for i in range(len(tabs)):
                    entity_dict[tabs[0]].add('.'.join(tabs[:(i+1)]))
    return entity_dict

# read old event types
def load_events(event_coarse, entity_dict):
    event_dict = {}
    for line in open(event_coarse):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if event_id not in event_dict:
                event_dict[event_id] = {}
                event_dict[event_id]['mention'] = {}
                event_dict[event_id]['args'] = {}
            if tabs[1] == 'type':
                event_dict[event_id]['type'] = prep_type_old(tabs[2])
            elif 'mention' in tabs[1]:
                event_dict[event_id]['mention'][tabs[2].replace("\"", "")] = tabs[3] # trigger -> offset, to find context
            elif 'mention' not in tabs[1]:
                arg_role = prep_arg_type_old(tabs[1])
                arg = tabs[2]
                event_dict[event_id]['args'][arg_role] = entity_dict[arg]
    return event_dict

# ps = PorterStemmer()
def trigger_lang_stem(trigger, offset, trans, lang, en_stemmer):
    # ->english
    if not lang.startswith('en'):
        trigger = trans[offset]
    # stem
    trigger = trigger.lower()
    if stemmer is not None:
        trigger_stem = stem_long(trigger, en_stemmer, 'en')
        return trigger_stem
    else:
        return trigger

# read fine-grained type rules
def load_type_dict(type_dict_path):
    for line in open(type_dict_path):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        old_type = tabs[0]
        new_type = tabs[1]
        arg_role = tabs[2]
        for arg_type in tabs[3].split(','):
            type_dict[old_type][arg_role][arg_type.strip()] = new_type
    return type_dict

# read trigger constraint
def load_trigger_dict(trigger_dict_path):
    stemmer = SnowballStemmer("english")
    for line in open(trigger_dict_path):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        old_type = tabs[0]
        new_type = tabs[1]
        for trigger_need in tabs[2].split(','):
            trigger_need = trigger_need.strip()
            trigger_need = stem_long(trigger_need, stemmer, 'en')
            trigger_dict[old_type][trigger_need] = new_type
    return trigger_dict

lemmer = WordNetLemmatizer()
def lemma_long(trigger):
    return ' '.join([lemmer.lemmatize(trigger_sub) for trigger_sub in trigger.split(' ')])
# read context constraint
def load_context_dict(context_dict_path):
    # stemmer = SnowballStemmer("english") # dict is english
    for line in open(context_dict_path):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        old_type = tabs[0]
        new_type = tabs[1]
        for context_need in tabs[2].split(','):
            context_need = context_need.strip()
            context_need = lemma_long(context_need)
            context_dict[old_type][context_need] = new_type
    return context_dict

# change type
def update_type(event_id, event_dict, type_dict, trigger_dict, context_dict, ltf_util, trans, lang, stemmer, en_stemmer):
    all_source_voter = Counter()

    # print(event_dict[event_id])

    old_type = event_dict[event_id]['type']
    if old_type in newtype_mapping_sure:
        return newtype_mapping_sure[old_type]
    if old_type in delete_type_sure:
        return None

    # by type
    new_types_by_arg = defaultdict(int)
    for arg_role in type_dict[old_type]:
        if arg_role in event_dict[event_id]['args']:
            if old_type == 'Life.Die' and (arg_role == 'Agent' or arg_role == 'Instrument'):
                return 'Life.Die.DeathCausedByViolentEvents'
            elif old_type == 'Life.Injure' and (arg_role == 'Agent' or arg_role == 'Instrument'):
                return 'Life.Injure.IllnessDegradationPhysical'
            arg_types = event_dict[event_id]['args'][arg_role]
            for arg_type in arg_types:
                # mutliple types
                if arg_type in type_dict[old_type][arg_role]:
                    aida_type = type_dict[old_type][arg_role][arg_type]
                    new_types_by_arg[aida_type] += 1
    new_types_by_arg_sorted = sorted(new_types_by_arg.items(), key=lambda x: (len(x[0].split('.')), x[1]),
                                       reverse=True)
    # print('arg-based: ', new_types_by_arg_sorted)
    if len(new_types_by_arg_sorted) > 0:
        max_type, max_score = new_types_by_arg_sorted[0]
        for each_type, each_score in new_types_by_arg_sorted:
            if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += 1

    # by trigger
    new_types_by_trgger = defaultdict(int)
    new_types_by_context = defaultdict(int)
    for trigger in event_dict[event_id]['mention']:
        # only one offset, before coreference
        offset = event_dict[event_id]['mention'][trigger]
        trigger_stem = trigger_lang_stem(trigger, offset, trans, lang, en_stemmer)
        if trigger_stem in trigger_dict[old_type]:
            aida_type = trigger_dict[old_type][trigger_stem]
            new_types_by_trgger[aida_type] += 1
            # return trigger_dict[old_type][trigger_stem]
            # print(trigger, old_type, aida_type)
        # if trigger == 'fire' and 'set fire not in the sentence':


        # if lang == 'en':
        context_sent = ' '.join(ltf_util.get_context(offset)).lower()
        # context_sent = stem_long(context_sent, stemmer, lang)
        context_sent = lemma_long(context_sent)
        for context_symbol in context_dict[old_type]:
            if ' '+context_symbol+' ' in context_sent:
                aida_type = context_dict[old_type][context_symbol]
                new_types_by_context[aida_type] += 1
                # print(trigger, context_symbol, old_type, aida_type, context_sent)

        if trigger_stem == 'fire' and old_type == 'Conflict.Attack':
            if stem_long('set fire', en_stemmer, 'en') not in context_sent:
                aida_type = 'Conflict.Attack.FirearmAttack'
                all_source_voter[aida_type] += 1
            else:
                aida_type = 'Conflict.Attack.SetFire'
                all_source_voter[aida_type] += 1

            # print(trigger, old_type, aida_type)
        # context_words = ltf_util.get_context(offset)
        # for context_word in context_words:
        #     context_word = stem_long(context_word, stemmer, lang)
        #     if context_word in context_dict[old_type]:
        #         aida_type = context_dict[old_type][context_word]
        #         new_types_by_context[aida_type] += 1
        #         # return context_dict[old_type][context_word]

    new_types_by_trgger_sorted = sorted(new_types_by_trgger.items(), key=lambda x: (len(x[0].split('.')), x[1]),
                                     reverse=True)
    # print('trigger-based: ', new_types_by_trgger_sorted)
    if len(new_types_by_trgger_sorted) > 0:
        max_type, max_score = new_types_by_trgger_sorted[0]
        for each_type, each_score in new_types_by_trgger_sorted:
            if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += 1

    new_types_by_context_sorted = sorted(new_types_by_context.items(), key=lambda x: (len(x[0].split('.')), x[1]),
                                        reverse=True)
    # print('context-based: ', new_types_by_context_sorted)
    if len(new_types_by_context_sorted) > 0:
        max_type, max_score = new_types_by_context_sorted[0]
        for each_type, each_score in new_types_by_context_sorted:
            if each_score == max_score and len(max_type.split('.')) == len(each_type.split('.')):
                all_source_voter[each_type] += 1

    if len(all_source_voter) == 0:
        # not find
        if old_type in delete_type_notsure:
            # print('\nno fine-grained type')
            return None
        else:
            return newtype_mapping_backup[old_type]
    newtype = all_source_voter.most_common(1)[0][0]
    # print('\nfinal fine-grained type', old_type, '->', all_source_voter.most_common(1))
    # print('\n=====================================\n')
    return newtype

def update_type_all(event_dict, type_dict, trigger_dict, context_dict, ltf_util, trans, lang, stemmer, en_stemmer):
    for event_id in event_dict:
        newtype = update_type(event_id, event_dict, type_dict, trigger_dict, context_dict, ltf_util, trans, lang, stemmer, en_stemmer)
        if newtype is not None:
            event_newtype[event_id] = newtype
            # print(event_dict[event_id]['mention'])
    return event_newtype

def rewrite(event_newtype, event_coarse, output):
    f_out = open(output, 'w')
    deleted_events = set()
    for line in open(event_coarse):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if event_id in deleted_events:
                continue
            if event_id not in event_newtype:
                # print(event_id, 'deleted')
                deleted_events.add(event_id)
                continue
            # print(event_id)
            newtype = event_newtype[event_id]
            if tabs[1] == 'type':
                f_out.write('%s\t%s\t%s%s\n' % (event_id, 'type', prefix, newtype))
                continue
            elif len(tabs) > 4 and 'mention' not in tabs[1]:# elif 'https:' in tabs[1]:
                old_role = tabs[1][tabs[1].find('_')+1:]
                # print(arg_mapping[newtype])
                if newtype in arg_mapping:
                    if old_role in arg_mapping[newtype]:
                        newrole = arg_mapping[newtype][old_role]
                    else:
                        newrole = old_role
                else:
                    parent_type = newtype[:newtype.rfind('.')]
                    # print('parent_type', parent_type)
                    if parent_type in arg_mapping:
                        if old_role in arg_mapping[parent_type]:
                            newrole = arg_mapping[parent_type][old_role]
                        else:
                            newrole = old_role
                    else:
                        newrole = old_role
                if newrole != 'None':
                    f_out.write('%s\t%s%s_%s\t%s\t%s\t%s\n' %
                                (event_id, prefix, newtype, newrole,
                                 tabs[2].replace(':Filler_', ':Entity_Filler_'), tabs[3], tabs[4]))
                continue
            f_out.write('%s\n' % line)
    print('Events deleted: ', len(deleted_events))
    ## argument role update!!!!
    f_out.close()

def load_trans(trans_file, lang):
    trans = {}
    if lang.startswith('en'):
        return trans
    for line in open(trans_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        if len(tabs) == 2:
            trans[tabs[0]] = tabs[1]
        else:
            if len(line) != 0:
                print('[ERROR] tranlation file can not separated by <offset - word>', line)
    return trans


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('lang', type=str,
                        help='lang.')
    parser.add_argument('ltf_dir', type=str,
                        help='ltf_dir')
    parser.add_argument('entity_finegrain', default=str,
                        help='entity_finegrain')
    parser.add_argument('entity_freebase_tab', type=str,
                        help='entity_freebase_tab')
    parser.add_argument('entity_coarse', default=str,
                        help='entity_coarse')
    parser.add_argument('event_coarse', default=str,
                        help='event_coarse')
    # parser.add_argument('output_dir', default=str, help='output')
    parser.add_argument('output', default=str,
                        help='output')
    parser.add_argument('--visualpath', default=None,
                        help='visualpath')
    parser.add_argument('--trans_file', type=None,
                        help='trans_file')
    parser.add_argument('--filler_coarse', type=None,
                        help='filler_coarse')
    parser.add_argument('--entity_finegrain_aida', type=None,
                        help='entity_finegrain_aida')

    args = parser.parse_args()

    lang = args.lang
    ltf_dir = args.ltf_dir
    entity_finegrain = args.entity_finegrain
    entity_freebase_tab = args.entity_freebase_tab
    entity_coarse = args.entity_coarse
    filler_coarse = args.filler_coarse
    event_coarse = args.event_coarse
    trans_file = args.trans_file
    output = args.output
    visualpath = args.visualpath
    entity_finegrain_aida = args.entity_finegrain_aida
    # output_dir = args.output_dir
    # output = os.path.join(output_dir, 'events_%s_fine.cs' % lang)
    # visualpath = os.path.join(output_dir, 'events_%s_fine.html' % lang)



    # lang = 'en'
    # entity_finegrain = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.corf.fine.json' % (lang, lang)
    # # entity_finegrain = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.fine.json' % (lang, lang)
    # entity_coarse = '/nas/data/m1/lim22/aida2019/dryrun/0322/%s/edl/merged.cs' % lang ##(?? not the final seedling type)
    # # entity_coarse = '/nas/data/m1/panx2/tmp/aida/eval/2019/%s/0322/%s.linking.cs' % (lang, lang)
    # filler_coarse = '/nas/data/m1/lud2/AIDA/dryrun/201905/filler/%s/filler_%s_cleaned.cs' % (lang, lang)
    # event_coarse = '/nas/data/m1/lim22/aida2019/dryrun/0322/%s/event/events_tme.cs' % lang
    # # event_coarse = '/nas/data/m1/subbua/dryrun0322/cs/%s_dryrun_0322.cs' % lang
    # output = '/nas/data/m1/lim22/aida2019/dryrun/0322/%s/event/events_%s_fine.cs' % (lang, lang)
    # visualpath = '/nas/data/m1/lim22/aida2019/dryrun/0322/%s/event/events_%s_fine.html' % (lang, lang)

    # ltf_dir = '/nas/data/m1/lim22/aida2019/dryrun/source/%s' % lang
    ltf_util = LTF_util(ltf_dir)

    # trans_file = '/nas/data/m1/lim22/aida2019/dryrun/source/%s.bio_trans' % lang
    # if trans_file is not None and len(trans_file) != 0:
    trans = load_trans(trans_file, lang)
    # print(trans)

    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    type_dict_path = os.path.join(CURRENT_DIR, 'rules/type_dict.txt')
    trigger_dict_path = os.path.join(CURRENT_DIR, 'rules/trigger_dict_clean_v2.txt')
    context_dict_path = os.path.join(CURRENT_DIR, 'rules/context_dict.txt')
    hierarchy_dir = os.path.join(CURRENT_DIR, '../../aida_edl/conf/yago_taxonomy_wordnet_single_parent.json')
    finetype_util = FineGrainedUtil(hierarchy_dir)
    entity_dict = finetype_util.entity_finegrain_by_json(entity_finegrain, entity_freebase_tab, entity_coarse,
                                                         filler_coarse)

    entity_dict = entity_finegrain_by_cs(entity_finegrain_aida, entity_dict)

    # print(entity_dict)
    stemmer = load_stemmer(lang)
    en_stemmer = load_stemmer('en')

    event_dict = load_events(event_coarse, entity_dict)
    print('event_dict', len(event_dict))
    type_dict = load_type_dict(type_dict_path)
    # print(type_dict)
    trigger_dict = load_trigger_dict(trigger_dict_path)
    # print(trigger_dict)
    context_dict = load_context_dict(context_dict_path)
    # print(context_dict)

    event_newtype = update_type_all(event_dict, type_dict, trigger_dict, context_dict, ltf_util, trans, lang, stemmer, en_stemmer)
    rewrite(event_newtype, event_coarse, output)

    if args.visualpath is not None:
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

        f_html = open(visualpath, 'w')
        f_html.write('%s\n' % head)
        count = 0
        for event in event_newtype:
            for trigger in event_dict[event]['mention']:
                count = count + 1
                ###    print('Trigger: %s'%trigger[3], 'Argument: %s'%argument[3])
                f_html.write('<p>%d. Old Event type: %s;<br> New Event type: %s;<br> Trigger: %s;</p>' % ( #<br> Argument: %s; Argument Role: %s
                    count, event_dict[event]['type'], event_newtype[event], trigger))  # , event_dict[event]['type']
                sent_out = ltf_util.get_context(event_dict[event]['mention'][trigger])
                sent_out_new = []
                for word in sent_out:
                    if word == trigger:
                        word = '<span style="color:blue">' + word + '</span>'
                    sent_out_new.append(word)
                f_html.write('<p>%s</p><br><br>' % (' '.join(sent_out_new)))
                # one trigger ##(??? multiple trigger?) -> no coreference, so not yet
                continue
        f_html.flush()
        f_html.close()

    print("Fine-grained event typing done for ", lang)