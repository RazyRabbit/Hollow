from itertools import zip_longest, count
from operator import itemgetter

import re

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

def compare(source, string):
    for a, b, score in zip_longest(source, string, count()):
        if a != b:
            return score

    return

def find(sources, string, reverse=True):
    return dict(sorted(zip(sources, (compare(str(source), string) for source in sources)), key=itemgetter(1), reverse=reverse))

def replace_escapes(line, replacement=''):
    return ansi_escape.sub(replacement, line)