from collections import defaultdict
import argparse
import os
import sys
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CURRENT_DIR, ".."))
from util.ltf_util import LTF_util

from nltk.stem.snowball import SnowballStemmer, PorterStemmer
from nltk.stem import WordNetLemmatizer
from pymystem3 import Mystem

# lemmatizer = WordNetLemmatizer()
# stemmer = PorterStemmer()

prefix = "https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#"


def load_lemmer(lang):
    if lang.startswith('en'):
        lemmer = WordNetLemmatizer()
        return lemmer
    elif lang.startswith('ru'):
        lemmer = Mystem()
        return lemmer
    elif lang.startswith('uk'):
        stemmer = dict()
        for line in open(os.path.join(CURRENT_DIR, 'rules', 'lemmatization-uk.txt')):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 2:
                stemmer[tabs[0]] = tabs[1]
        return stemmer
    else:
        return None


def lemma_long(trigger, lemmer, lang):
    if lang.startswith('en'):
        return ' '.join([lemmer.lemmatize(trigger_sub) for trigger_sub in trigger.split(' ')])
    elif lang.startswith('ru'):
        return ' '.join(lemmer.lemmatize(trigger))
    elif lang.startswith('uk'):
        toks = []
        for trigger_sub in trigger.split(' '):
            if trigger_sub in lemmer:
                toks.append(lemmer[trigger_sub])
            else:
                toks.append(trigger_sub)
        return ' '.join(toks)
    else:
        return trigger


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
        for line in open(os.path.join(CURRENT_DIR, 'rules', 'lemmatization-uk.txt')):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            if len(tabs) == 2:
                stemmer[tabs[0]] = tabs[1]
        return stemmer
    else:
        return None


def load_arg_mapping(mapping_arg_file):
    mapping = defaultdict(lambda: defaultdict(str))
    for line in open(mapping_arg_file):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        # if len(tabs) == 3:
        #     # newtype -> original role -> new role
        mapping[tabs[0]][tabs[1]] = tabs[2]
        # else:
        #     print(line)
    return mapping


# read trigger constraint
def load_trigger_dict(trigger_dict_path, stemmer, lang):
    trigger_dict = defaultdict(lambda: defaultdict(str))
    # stemmer = SnowballStemmer("english")
    for line in open(trigger_dict_path):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        old_type = tabs[0]
        new_type = tabs[1]
        for trigger_need in tabs[2].split(','):
            trigger_need = trigger_need.strip()
            trigger_need = stem_long(trigger_need, stemmer, lang)
            trigger_dict[old_type][trigger_need] = new_type
    return trigger_dict

def need_update_types(event_coarse, stemmer, lang, ltf_util, trigger_dict_path, context_dict):
    trigger_type_dict = load_trigger_dict(trigger_dict_path, stemmer, lang)
    trigger_shot_str = {'en': 'shot', 'ru': 'выстрел', 'uk': 'постріл'}
    trigger_bomb_str = {'en': 'bomb', 'ru': 'бомбить', 'uk': 'бомба'}
    trigger_bombing_str = {'en': 'bombing', 'ru': 'бомбардировка', 'uk': 'бомбардування'}
    trigger_blasts_str = {'en': 'blasts', 'ru': 'взрывы', 'uk': 'вибухи'}
    trigger_bombblast_str = {'en': 'bomb blast', 'ru': 'взрыв бомбы', 'uk': 'вибух бомби'}
    trigger_shootout_str = {'en': 'shoot out', 'ru': 'стрелять', 'uk': 'вистрілити'}
    trigger_purchased_str = {'en': 'purchased', 'ru': 'купленный', 'uk': 'придбано'}
    trigger_trafficking_str = {'en': 'trafficking', 'ru': 'торговля', 'uk': 'торгівля людьми'}
    trigger_murders_str = {'en': 'murders', 'ru': 'убийства', 'uk': 'вбивства'}
    trigger_passedoff_str = {'en': 'passed off', 'ru': 'прошло', 'uk': 'відійшов'}


    # event_type_trigger = defaultdict(set)
    offset2trigger = defaultdict()
    event_type_trigger_offset = defaultdict(set)
    for line in open(event_coarse):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if tabs[1] == 'mention.actual':
                # event_type_trigger[event_id].add(tabs[2][1:-1])
                offset2trigger[tabs[3]] = tabs[2][1:-1]
                event_type_trigger_offset[event_id].add(tabs[3])

    need_update_type = {}
    for line in open(event_coarse):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if tabs[1] == 'type':
                event_type = tabs[2].split('#')[-1]

                for trigger_offset in event_type_trigger_offset[event_id]:
                    trigger = offset2trigger[trigger_offset]
                    # if not lang.startswith('en'):
                    #     trigger = trans[trigger_offset]

                    trigger_lemma = stem_long(trigger, stemmer, lang)
                    for trigger_dict in trigger_type_dict[event_type]:
                        if trigger_lemma == trigger_dict:
                            need_update_type[event_id] = trigger_type_dict[event_type][trigger_dict]
                            break
                    # print(trigger_lemma)
                    if event_id not in need_update_type:
                        trigger_expand = ' '.join(ltf_util.get_expand_text(trigger_offset, 2))
                        # if not lang.startswith('en'):
                        #     trigger_expand = trans_long[trigger_offset]
                        trigger_expand = stem_long(trigger_expand, stemmer, lang)
                        for trigger_dict in trigger_type_dict[event_type]:
                            if len(trigger_dict.split()) > 1:
                                if trigger_dict in trigger_expand:
                                    need_update_type[event_id] = trigger_type_dict[event_type][trigger_dict]
                                    break

                    # if event_id not in need_update_type:
                    if event_type in context_dict:
                        aida_type = None
                        for context_symbol in context_dict[event_type]:
                            if ' ' + context_symbol + ' ' in trigger_expand:
                                aida_type = context_dict[event_type][context_symbol]
                                # print(event_type, aida_type, context_symbol)
                        if aida_type is not None:
                            need_update_type[event_id] = aida_type

                    if event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_shot_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.FirearmAttack'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_bomb_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.Bombing'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_bombing_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.Bombing'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long('Bomb', stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.Bombing'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_blasts_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.Bombing'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_bombblast_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.Bombing'
                    elif event_type == 'Conflict.Attack' and stem_long(trigger, stemmer, lang) == stem_long(trigger_shootout_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Conflict.Attack.FirearmAttack'
                    elif event_type == 'Transaction.TransferOwnership' and stem_long(trigger, stemmer, lang) == stem_long(trigger_purchased_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Transaction.TransferOwnership.Purchase'
                    elif event_type == 'Life.Die' and stem_long(trigger, stemmer, lang) == stem_long(trigger_passedoff_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Life.Die.NonviolentDeath'
                    elif event_type == 'Movement.TransportPerson' and stem_long(trigger, stemmer, lang) == stem_long(trigger_trafficking_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Movement.TransportPerson.SmuggleExtract'
                    elif event_type == 'Life.Die' and stem_long(trigger, stemmer, lang) == stem_long(trigger_murders_str[lang], stemmer, lang):
                        need_update_type[event_id] = 'Life.Die.DeathCausedByViolentEvents'
            elif 'https:' in tabs[1]:
                old_role = tabs[1][tabs[1].find('_')+1:].replace(".actual", "")
                if old_role == 'None':
                    continue
                if event_type == 'Life.Die' and (old_role == 'Killer' or old_role == 'Agent' or old_role == 'Instrument'):
                    need_update_type[event_id] = 'Life.Die.DeathCausedByViolentEvents'
                elif event_type.startswith('Life.Injure') and (old_role == 'Agent' or old_role == 'Injurer' or old_role == 'Instrument'):
                    need_update_type[event_id] = 'Life.Injure.InjuryCausedByViolentEvents'

    # print(need_update_type)
    return need_update_type

def delete_event_list(event_fine, ltf_util):

    events_del = set()

    event_type_dict = dict()
    event_have_args = set()
    for line in open(event_fine):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if tabs[1] == 'type':
                event_type_dict[event_id] = tabs[2].split('#')[-1]
            if 'http' in tabs[1]:
                event_have_args.add(event_id)

    for line in open(event_fine):
        if line.startswith(':Event'):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            event_id = tabs[0]
            if tabs[1] == 'mention.actual':
                trigger = tabs[2][1:-1]
                if trigger == 'fell' and event_type_dict[event_id] == 'Transaction.Transaction':
                    events_del.add(event_id)
                if trigger == 'took' and event_type_dict[event_id] == 'Transaction.Transaction':
                    events_del.add(event_id)
                if trigger == 'fell' and event_type_dict[event_id] == 'Transaction.Transaction.TransferControl':
                    events_del.add(event_id)
                if trigger.startswith('pollut') and event_type_dict[event_id].startswith('Government.Vote'):
                    events_del.add(event_id)
                if trigger == 'took' and event_type_dict[event_id] == 'Transaction.Transaction.TransferControl':
                    context = ltf_util.get_context(tabs[3])
                    if 'took control of' not in context and \
                        'took over' not in context and \
                        'took command of' not in context:
                        events_del.add(event_id)
                if trigger == 'take' and event_type_dict[event_id] == 'Transaction.Transaction.TransferControl':
                    context = ltf_util.get_context(tabs[3])
                    if 'take control of' not in context and \
                        'take over' not in context and \
                        'take command of' not in context:
                        events_del.add(event_id)
                if trigger == 'taken' and event_type_dict[event_id] == 'Transaction.Transaction.TransferControl':
                    context = ltf_util.get_context(tabs[3])
                    if 'taken control of' not in context and \
                        'taken over' not in context and \
                        'taken command of' not in context:
                        events_del.add(event_id)
                if trigger.lower().startswith('sign') and event_type_dict[event_id] == 'Government.Agreements.AcceptAgreementContractCeasefire':
                    events_del.add(event_id)
                if event_type_dict[event_id] == 'Government.Formation' and event_id not in event_have_args:
                    events_del.add(event_id)

    return events_del

def filter_roles(new_line):
    if 'Movement.TransportPerson.PreventEntry_Vehicle' in new_line or \
            'Movement.TransportPerson.GrantEntryAsylum_Vehicle' in new_line or \
            'Movement.TransportPerson.Fall_Vehicle' in new_line or \
            'Movement.TransportArtifact.Fall_Transporter' in new_line:
        return None

    new_line = new_line.replace(
        "Movement.TransportPerson.SelfMotion_Passenger",
        "Movement.TransportPerson.SelfMotion_Transporter"
    ).replace(
        'Movement.TransportPerson.Fall_Transporter',
        'Movement.TransportPerson.Fall_Passenger'
    ).replace(
        'Transaction.Transaction.EmbargoSanction_Participant',
        'Transaction.Transaction.EmbargoSanction_Preventer'
    ).replace(
        'Contact.Discussion.Broadcast',
        'Contact.PublicStatementInPerson.Broadcast'
    ).replace(
        'Contact.CommitmentPromiseExpressIntent.Broadcast_Broadcaster',
        'Contact.CommitmentPromiseExpressIntent.Broadcast_Communicator'
    ).replace(
        'Contact.MediaStatement.Broadcast_Participant',
        'Contact.MediaStatement.Broadcast_Communicator'
    ).replace(
        'Contact.MediaStatement.Broadcast_Broadcaster',
        'Contact.MediaStatement.Broadcast_Communicator'
    ).replace(
        'Contact.RequestAdvise.Broadcast_Participant',
        'Contact.RequestAdvise.Broadcast_Communicator'
    ).replace(
        'Contact.RequestAdvise.Broadcast_Broadcaster',
        'Contact.RequestAdvise.Broadcast_Communicator'
    ).replace(
        'Contact.MediaStatement.Broadcast_Broadcast_Communicator',
        'Contact.MediaStatement.Broadcast_Communicator'
    ).replace(
        'Contact.CommandOrder.Broadcast_Broadcaster',
        'Contact.CommandOrder.Broadcast_Communicator'
    ).replace(
        'Contact.CommandOrder.Broadcast_Participant',
        'Contact.CommandOrder.Broadcast_Communicator'
    ).replace(
        'Contact.PublicStatementInPerson.Broadcast_Broadcaster',
        'Contact.PublicStatementInPerson.Broadcast_Communicator'
    ).replace(
        'ArtifactExistence.DamageDestroy_Victim',
        'ArtifactExistence.DamageDestroy_Artifact'
    ).replace(
        'Contact.PublicStatementInPerson.Broadcast_Participant',
        'Contact.PublicStatementInPerson.Broadcast_Communicator'
    ).replace(
        'Contact.CommitmentPromiseExpressIntent_Participant',
        'Contact.CommitmentPromiseExpressIntent_Communicator'
    ).replace(
        'Contact.ThreatenCoerce.Broadcast_Broadcaster',
        'Contact.ThreatenCoerce.Broadcast_Communicator'
    ).replace(
        "Transaction.Transaction.GiftGrantProvideAid_Participant",
        "Transaction.Transaction.GiftGrantProvideAid_Giver"
    ).replace(
        'Justice.JudicialConsequences.Extradite_Place',
        'Justice.JudicialConsequences.Extradite_Origin'
    ).replace(
        'Justice.JudicialConsequences.Extradite_Adjudicator',
        'Justice.JudicialConsequences.Extradite_Extraditer'
    ).replace(
        'Justice.JudicialConsequences.Convict_Person',
        'Justice.JudicialConsequences.Convict_Defendant'
    ).replace(
        'Justice.JudicialConsequences.Extradite_JudgeCourt',
        'Justice.JudicialConsequences.Extradite_Extraditer'
    ).replace(
        'Contact.Discussion.Meet_Communicator',
        'Contact.Discussion.Meet_Participant'
    ).replace(
        'Movement.TransportPerson.Hide_Person',
        'Movement.TransportPerson.Hide_Passenger'
    ).replace(
        'Contact.Discussion.Correspondence_Broadcaster',
        'Contact.Discussion.Correspondence_Communicator'
    ).replace(
        'Contact.Discussion.Correspondence_Audience',
        'Contact.Discussion.Correspondence_Recipient'
    ).replace(
        'Contact.CommandOrder_Participant',
        'Contact.CommandOrder_Communicator'
    ).replace(
        'Transaction.TransferMoney.EmbargoSanction_Beneficiary',
        'Transaction.TransferMoney.EmbargoSanction_Recipient'
    ).replace(
        'Justice.JudicialConsequences.Convict_Agent',
        'Justice.JudicialConsequences.Convict_JudgeCourt'
    ).replace(
        'Movement.TransportArtifact.PreventExit_Vehicle',
        'Movement.TransportArtifact.PreventExit_Artifact'
    )
    return new_line

def rewrite(event_coarse, output, ltf_dir, stemmer, lang, trigger_dict_path, context_dict):
    ltf_util = LTF_util(ltf_dir)

    events_del = delete_event_list(event_coarse, ltf_util)

    need_update_type = need_update_types(event_coarse, stemmer, lang, ltf_util, trigger_dict_path, context_dict)
    arg_mapping = load_arg_mapping(os.path.join(CURRENT_DIR, 'rules', 'mapping_args.txt'))
    f_out = open(output, 'w')
    for line in open(event_coarse):
        if line.startswith(':Event'):
            line = line.rstrip('\n')

            if 'Contact.Discussion.Broadcast' in line:
                print(line)

            tabs = line.split('\t')
            event_id = tabs[0]
            if event_id in events_del:
                continue
            if 'mention' in tabs[1]:
                trigger_offset = tabs[3]
            if tabs[1] == 'type':
                newtype = tabs[2].replace(prefix, "")
                if event_id in need_update_type:
                    newtype = need_update_type[event_id]
                f_out.write('%s\ttype\t%s%s\n' % (event_id, prefix, newtype))
                continue
            elif 'https:' in tabs[1]:

                old_role = tabs[1][tabs[1].find('_')+1:].replace(".actual", "")
                # if old_role == 'Time':
                #     f_out.write('%s\ttime\t%s\t%s\t%s\n' %
                #                 (event_id, tabs[2].replace(':Filler_', ':Entity_Filler_'),
                #                  tabs[3], tabs[4]))
                #     continue
                if old_role == 'None':
                    continue
                if newtype in arg_mapping:
                    if old_role in arg_mapping[newtype]:
                        newrole = arg_mapping[newtype][old_role]
                    else:
                        newrole = old_role
                else:
                    parent_type = newtype[:newtype.rfind('.')]
                    if parent_type in arg_mapping:
                        if old_role in arg_mapping[parent_type]:
                            newrole = arg_mapping[parent_type][old_role]
                        else:
                            newrole = old_role
                    else:
                        newrole = old_role
                    if newtype.startswith('Contact.RequestAdvise') or \
                            newtype.startswith('Contact.CommandOrder') or \
                            newtype.startswith('Contact.PublicStatementInPerson') or \
                            newtype.startswith('Contact.MediaStatement') or \
                            newtype.startswith('Contact.ThreatenCoerce'):
                        role_offset = tabs[3]
                        begin = int(role_offset.split(':')[1].split('-')[0])
                        end = int(role_offset.split(':')[1].split('-')[1])
                        trigger_offset_end = int(trigger_offset.split(':')[1].split('-')[1])
                        if begin > trigger_offset_end:
                            newrole = 'Recipient'
                        else:
                            newrole = 'Communicator'
                if newrole != 'None':
                    new_line = ('%s\t%s%s_%s.actual\t%s\t%s\t%s\n' %
                                (event_id, prefix, newtype, newrole, tabs[2].replace(':Filler_', ':Entity_Filler_'), tabs[3], tabs[4]))
                    new_line = filter_roles(new_line)
                    if new_line is not None:
                        f_out.write(new_line)
                continue
        new_line = filter_roles(line)
        if new_line is not None:
            f_out.write('%s\n' % line.replace(':Filler_', ':Entity_Filler_'))
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


def load_context_dict(context_dict_path, stemmer, lang):
    # stemmer = SnowballStemmer("english") # dict is english
    context_dict = defaultdict(lambda : defaultdict())
    for line in open(context_dict_path):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        old_type = tabs[0]
        new_type = tabs[1]
        for context_need in tabs[2].split(','):
            context_need = context_need.strip()
            context_need = stem_long(context_need, stemmer, lang)
            context_dict[old_type][context_need] = new_type
    return context_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str,
                        help='input event file')
    parser.add_argument('ltf_dir', type=str,
                        help='ltf_dir')
    parser.add_argument('output', type=str,
                        help='output event file')
    parser.add_argument('lang', type=str,
                        help='input event file')
    # parser.add_argument('trans_file', type=str, default="",
    #                     help='input event file')
    # parser.add_argument('trans_file_long', type=str, default="",
    #                     help='input event file')

    args = parser.parse_args()

    lang = args.lang

    stemmer = load_stemmer(lang)
    trigger_dict_path = os.path.join(CURRENT_DIR, 'rules', '%s_trigger_dict_clean_v2.txt' % lang)
    context_dict_path = os.path.join(CURRENT_DIR, 'rules', '%s_context_dict.txt' % lang)
    context_dict = load_context_dict(context_dict_path, stemmer, lang)
    rewrite(args.input, args.output, args.ltf_dir, stemmer, lang, trigger_dict_path, context_dict)
    ## number exact equal