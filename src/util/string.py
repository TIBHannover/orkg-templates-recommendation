import os
import re


def uri_to_id(uri):
    return os.path.basename(uri)


def id_to_uri(id):
    return 'http://orkg.org/orkg/resource/{}'.format(id)


def post_process(string):
    if not string:
        return string

    # replace each occurrence of one of the following characters with ' '
    characters = ['\s+-\s+', '-', '_', '\.']
    regex = '|'.join(characters)
    string = re.sub(regex, ' ', string)

    return ' '.join(string.split()).lower()


def create_sequence(sentence_1, sentence_2):
    return '[CLS] {} [SEP] {} [SEP]'.format(sentence_1, sentence_2)


def extend_path(path, extension):
    dir_name = os.path.split(path)[0]
    file_name = os.path.splitext(os.path.split(path)[1])[0] + extension
    file_extension = os.path.splitext(os.path.split(path)[1])[1]
    extended_file_name = os.path.join(dir_name, file_name + file_extension)
    return extended_file_name
