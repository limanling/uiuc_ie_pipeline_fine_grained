from nltk.parse.stanford import StanfordDependencyParser
from nltk.tag import StanfordPOSTagger
from nltk.parse.corenlp import CoreNLPParser
from utils.common.io import read_dict_from_json_file

class StanfordNLTKWrapper:
    def __init__(self, config_file_path='aida_event/config/xmie.json'):
        self._config = read_dict_from_json_file(config_file_path)
        self._domain_name = self._config['common_tools']['stanford_url']
        self._port_number = self._config['common_tools']['stanford_port']
        self._pos_model = self._config['common_tools']['stanford_pos_model']
        self._pos_jar = self._config['common_tools']['stanford_pos_jar']
        self._parser_model = self._config['common_tools']['stanford_parser_model']
        self._parser_jar = self._config['common_tools']['stanford_parser_jar']

        self._core_nlp_parser = CoreNLPParser(url='%s:%s' % (self._domain_name, self._port_number))
        self._pos_tagger = StanfordPOSTagger(model_filename=self._pos_model,
                                             path_to_jar=self._pos_jar)
        self._dep_parser = StanfordDependencyParser(path_to_jar=self._parser_jar,
                                                   path_to_models_jar=self._parser_model,
                                                   java_options='-Xmx16G')

    def tokenizer(self, input_text):
        return list(self._core_nlp_parser.tokenize(input_text))

    def pos_tag(self, input_tokenized_sentence):
        return self._pos_tagger.tag(input_tokenized_sentence)

    def pos_tag_sentences(self, input_tokenized_sentences):
        return self._pos_tagger.tag_sents(input_tokenized_sentences)

    def dependency_parser(self, input_tokenized_pos_tagged_sentence):
        return self._dep_parser.tagged_parse(input_tokenized_pos_tagged_sentence)

    def dependency_parser_sentences(self, input_tokenized_pos_tagged_sentences):
        return self._dep_parser.tagged_parse_sents(input_tokenized_pos_tagged_sentences)