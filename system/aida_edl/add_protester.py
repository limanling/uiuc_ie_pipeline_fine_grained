from collections import defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('coarse_event_cs', type=str, help='coarse_event_cs')
parser.add_argument('input_cs', type=str, help='input cold start')
parser.add_argument('output_cs', default=str, help='output_cs')
args = parser.parse_args()

coarse_event_cs = args.coarse_event_cs
entity_fine_grained = args.input_cs # '/nas/data/m1/lim22/aida2019/TA1b_eval/E101_PT003/en_all/edl/entity_fine_fixed8.cs'
# coarse_event_cs = '/data/m1/huangl7/AIDA/E101PT003_1/en.event.cs'
output_cs = args.output_cs

type_prefix = 'https://tac.nist.gov/tracks/SM-KBP/2019/ontologies/LDCOntology#'
writer = open(output_cs, 'w')

demonstrate_offset = set()
for line in open(coarse_event_cs):
    if line.startswith(':Event'):
        tabs = line.split('\t')
        if 'mention' not in tabs[1] and 'type' not in tabs[1]:
            role = tabs[1].split('_')[-1].replace('.actual', '')
            if role == 'Demonstrator':
                offset = tabs[3]
                demonstrate_offset.add(offset)

entity_types = defaultdict(set)
entity_protester = set()
entity_protesterleader = set()
for line in open(entity_fine_grained):
    if line.startswith(':Entity'):
        line = line.rstrip('\n')
        tabs = line.split('\t')
        if 'mention' in tabs[1]:
            offset = tabs[3]
            if offset in demonstrate_offset:
                entity_protester.add(tabs[0])
                if 'leader' in tabs[2]:
                    entity_protesterleader.add(tabs[0])
        elif 'type' in tabs[1]:
            entity_types[tabs[0]].add(tabs[2].split('#')[-1])

# print(entity_protester)

for line in open(entity_fine_grained):
    line = line.rstrip('\n')
    found = False
    if line.startswith(':Entity'):
        tabs = line.split('\t')
        if 'type' in tabs[1]:
            entity_id = tabs[0]
            if entity_id in entity_protester and len(entity_types[entity_id]) == 1:
                for entity_type in entity_types[entity_id]:
                    if entity_type == 'PER':
                        if entity_id in entity_protesterleader:
                            writer.write('%s\ttype\t%s%s\t%.6f\n' % (tabs[0], type_prefix, 'PER.Protester.ProtestLeader', 0.5))
                        else:
                            writer.write('%s\ttype\t%s%s\t%.6f\n' % (tabs[0], type_prefix, 'PER.Protester', 0.7))
                        found = True
                        # print(tabs[0])
    if not found:
        writer.write('%s\n' % line)

writer.flush()
writer.close()