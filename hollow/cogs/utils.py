from itertools import zip_longest, count
from operator import itemgetter

def compare(source, string):
    for a, b, score in zip_longest(source, string, count()):
        if a != b:
            return score

    return

def find(sources, string, reverse=True):
    return dict(sorted(zip(sources, (compare(str(source), string) for source in sources)), key=itemgetter(1), reverse=reverse))