from operator import itemgetter

def get_similarity(source, iterable):
    '''determina a similaridade entre dois iteraveis'''

    longest = source if len(source) > len(iterable) else iterable
    score = 0

    for elm_a, elm_b in zip(source, iterable):
        score += elm_a == elm_b
    
    return round(score/len(longest), 1)

def get_nearest(source, *iterables):
    '''retorna o iteravel mais proximo de source'''
    return max(((iterable, get_similarity(source, iterable)) for iterable in iterables), key=itemgetter(1))
