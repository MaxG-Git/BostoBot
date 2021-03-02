


def first(iterable, default, condition = lambda x: True, filter_true = None, filter_false = None):
    try:
        if filter_true == None:
            return next(x for x in iterable if condition(x))
        else:
            return filter_true(next(x for x in iterable if condition(x)))
    except StopIteration:
        if filter_false == None:
            return default
        else:
            return filter_false(default)

def flatten(iterables, filter_result=tuple):
    if filter_result == None:
        return (elem for iterable in iterables for elem in iterable)
    else:
        out = (elem for iterable in iterables for elem in iterable)
        return filter_result(out)