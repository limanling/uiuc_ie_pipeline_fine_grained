import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_cs', type=str,
                        help='input_cs')
    parser.add_argument('output_cs', type=str,
                        help='output_cs')

    args = parser.parse_args()

    with open(args.output_cs, 'w') as f_out:
        for line in open(args.input_cs):
            if line.startswith(':Event'):
                line = line.rstrip('\n')
                tabs = line.split('\t')
                event_id = tabs[0]
                if 'https:' in tabs[1]:
                    old_role = tabs[1][tabs[1].find('_') + 1:].replace(".actual", "")
                    if old_role == 'Time':
                        f_out.write('%s\ttime\t%s\t%s\t%s\n' %
                                    (event_id, tabs[2].replace(':Filler_', ':Entity_Filler_'),
                                     tabs[3], tabs[4]))
                        continue
            f_out.write('%s\n' % line)