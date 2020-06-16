import argparse

# class ParentChildUtil(object):
#     def __init__(self):
#         super(ParentChildUtil, self).__init__()
#
#     @staticmethod
def get_column_idx(sorted=True):
    if sorted: #parent_child_tab.endswith('.sorted.tab'):
        child_id_column = 2  # child_uid
        parent_id_column = 7  # parent_uid
        date_column = 3  # content_date
    else:
        child_id_column = 3  # child_uid
        parent_id_column = 2  # parent_uid
        date_column = 13  # content_date
    return child_id_column, parent_id_column, date_column


    # @staticmethod
def write_date4stanford(parent_child_file, output_file, sorted=True):
    child_id_column, parent_id_column, date_column = get_column_idx(sorted=sorted)
    with open(output_file, 'w') as writer:
        # child2date = dict()
        for line in open(parent_child_file):
            line = line.rstrip('\n')
            tabs = line.split('\t')
            # child2date[tabs[self.raw_id_column]] = tabs[self.date_column]
            writer.write('%s.rsd.txt\t%s\n' % (tabs[child_id_column], tabs[date_column]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('parent_child_mapping_file', type=str,
                        help='the parent_child mapping file path')
    parser.add_argument('parent_child_mapping_file_sorted', type=int,
                        help='1 if the parent_child mapping file is sorted.tab, otherwise 0')
    parser.add_argument('output_file', type=str,
                        help='output_file')
    args = parser.parse_args()

    write_date4stanford(args.parent_child_mapping_file, args.output_file, sorted=args.parent_child_mapping_file_sorted!=0)