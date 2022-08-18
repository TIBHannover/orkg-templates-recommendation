import re


class DocumentCreator:

    @staticmethod
    def create():
        raise NotImplementedError()

    @staticmethod
    def postprocess(string, is_query=False):
        if not string:
            return string

        # replace each occurrence of one of the following characters with ' '
        characters = ['\s+-\s+', '-', '_', '\.']
        regex = '|'.join(characters)
        string = re.sub(regex, ' ', string)

        # apply escaping for ES reserved characters
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#_reserved_characters
        if is_query:
            string = escape_es_query(string)

        # terms are lower-cased and only seperated by a space character
        return ' '.join(string.split()).lower()


escape_rules = {
    '+': r'\\+',
    '-': r'\\-',
    '&': r'\\&',
    '|': r'\\|',
    '!': r'\\!',
    '(': r'\\(',
    ')': r'\\)',
    '{': r'\\{',
    '}': r'\\}',
    '^': r'\\^',
    '~': r'\\~',
    '*': r'\\*',
    '"': r'\"',
    '/': r'\\/',
    '>': r' ',
    '<': r' '}


def escaped_seq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escape_rules.keys():
            yield escape_rules[char]
        else:
            yield char


def escape_es_query(query):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = query.replace('\\', r'\\')  # escape \ first
    return "".join([nextStr for nextStr in escaped_seq(term)])
