import argparse
import codecs
import os

def write_file(file_path, f_final):
    for one_line in codecs.open(file_path, 'r', 'utf-8'):
        one_line = one_line.strip()
        f_final.write('%s\n' % one_line)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Final output to ColdStart++ including all components')
    parser.add_argument("--cs_fnames", nargs="+",
                           help="List of paths to input CS files.", required=True)
    # parser.add_argument('-e', '--edl', help='EDL output file', required=True)
    # parser.add_argument('-f', '--filler', help='Filler output file', required=False)
    # parser.add_argument('-r', '--relation', help='Relation output file', required=False)
    # parser.add_argument('-n', '--newrelation', help='New relation output file', required=False)
    # parser.add_argument('-v', '--event', help='Event output file', required=False)
    parser.add_argument('-o', '--output_file', help='final output file', required=True)
    args = parser.parse_args()

    cs_fnames = args.cs_fnames
    print(cs_fnames)
    # edl_file_path = args['edl']
    # filler_file_path = args['filler']
    # relation_file_path = args['relation']
    # new_relation_file_path = args['newrelation']
    # event_file_path = args['event']
    # output_file_path = args['output_file']

    f_final = codecs.open(args.output_file, 'w', 'utf-8')

    # if args.edl:
    #     write_file(args.edl, f_final)
    # if args.filler:
    #     write_file(args.filler, f_final)
    # if args.relation:
    #     write_file(args.relation, f_final)
    # if args.newrelation:
    #     write_file(args.newrelation, f_final)
    # if args.event:
    #     write_file(args.event, f_final)
    for cs_fname in cs_fnames:
        write_file(cs_fname, f_final)

    f_final.flush()
    f_final.close()