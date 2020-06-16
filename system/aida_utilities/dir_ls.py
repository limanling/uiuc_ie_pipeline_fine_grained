import os
import sys
import codecs

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print(sys.argv)
        print('USAGE: python <dir> <output_file>')
        exit()
    indir = sys.argv[1]
    output_file = sys.argv[2]
    # cwd = os.path.dirname(os.path.realpath(__file__))
    with codecs.open(output_file, 'w', encoding='utf8') as writer:
        for file in os.listdir(os.path.join(indir)):
            writer.write(file)
            writer.write('\n')