from math import sqrt

'''
# Convention:
   1. LD == List Dictionary :: [dict]
   2. D == dictionary
   3. functions that act on LDs,
   4. have them as there last argument.
   5. no functions modify there arguments
   6. all functions functions are eger, not lazy.
'''


def by(key, LD):
    D_out = {}
    for D in LD:
        if not D[key] in D:
            D_out[D[key]] = []
        D_out[D[key]].append(D)
    return D_out


def get(*args):
    assert len(args) > 0, 'requiers at least one argument'

    if len(args) == 1:
        key = args[0]
        return lambda LD: list(map(lambda D: D[key], LD))

    LD = args[-1]
    keys = args[:-1]

    def getter(key):
        return list(map(lambda D: D[key], LD))

    if len(keys) == 1:
        key = keys[0]
        return getter(key)
    else:
        return [getter(key) for key in keys]


def get_keys(LD):
    return set.union(*[set(D) for D in LD])


def hermoginise(ld: [dict()], default=None):
    keys = get_keys(ld)
    new_ld = []
    for d in ld:
        new_ld.append({k: (d.get(k) or default) for k in keys})
    return new_ld


def split_by_quote(string: str):
    parts = []

    class Mode:
        normal = 0
        quote = 1
        escape = 2
        brackets = 3

    brackets = {'[': ']', '{': '}', '(': ')', '<': '>'}
    brackets_stack = []
    mode = Mode.normal
    buffer = ''
    for c in string:
        match mode:
            case Mode.normal:
                if c in brackets:
                    brackets_stack.append(brackets[c])
                elif len(brackets_stack) != 0 and c == brackets_stack[-1]:
                    brackets_stack.pop()

                if c == ',' and len(brackets_stack) == 0:
                    parts.append(buffer.strip())
                    buffer = ''
                    continue
                if c in {'"', "'"}:
                    if len(buffer) != 0 and len(brackets_stack) == 0:
                        parts.append(buffer.strip())
                        buffer = ''
                    quote_char = c
                    mode = Mode.quote
                    continue
                if c == '\\':
                    mode = Mode.escape
                    continue

                buffer += c

            case Mode.quote:
                if c in quote_char:
                    mode = Mode.normal
                    continue
                buffer += c

            case Mode.escape:
                mode = Mode.normal
                buffer += c
    if len(buffer) != 0:
        parts.append(buffer.strip())
    return parts


def from_csv(csv_string, header=None):

    match header:
        case str():
            keys = split_by_quote(header)
        case bool():
            header, *body = csv_string.split('\n')
        case list():
            keys = header
            body = csv_string.split('\n')
        case _:
            body = csv_string.split('\n')
            keys = list(range(len(split_by_quote(body[0]))))

    ld = []
    for line in body:
        if line.strip() == '':
            continue
        ld.append({k: v for k, v
                   in zip(keys, split_by_quote(line))})
        assert len(ld[-1]) == len(keys), 'Invalid CSV'
    return ld


def to_csv(LD: [dict]) -> str:
    keys = get_keys(LD)
    body = []
    for D in LD:
        body.append(',\t'.join([(str(D[k]) or '') for k in keys]))
    return ',\t'.join(keys) + '\n' + ',\t'.join(body)


def dict_map(foo, D):
    'map a function over the values of a dictionary'
    return {key: foo(value) for key, value in D.items()}


def list_dict_map(foo, LD):
    'map a function over the values of the dictionaries in a listdict'
    return list(map(lambda D: dict_map(foo, D), LD))


def transform(foodict, LD):
    '''Transfor a listdict by updateing the values of the constituant dictionaries in acordence with the function dictionary passed.
      { key:function }, [{ key:value }] => [{ key:function(value) }]'''
    if callable(foodict):
        foo = foodict
        foodict = {k: foo for k in get_keys(LD)}

    def update_dict(D):
        for key, foo in foodict.items():
            D = (D | {key: foo(D[key])}) if key in D else D
        return D
    return list(map(update_dict, LD)) if LD else update_dict


def join(*listdicts):
    def update(Ds):
        Agregate = dict()
        for D in Ds:
            Agregate.update(D)
        return Agregate
    return [update(Ds) for Ds in zip(*listdicts)]


def remove(*args):
    LD = args[-1]
    keys = args[:-1]
    new_LD = []
    for D in LD:
        new_LD.append({k: v for k, v in D.items()
                       if k not in keys})
    return new_LD


def load_yaml(filename):
    import yaml
    with open(filename, 'r') as f:
        return yaml.load(f, yaml.loader.SafeLoader)


def average(xs):
    'finds the mean of the input list'
    return sum(xs)/len(xs)


def sort_list_dict(key, listdict, reverse=False):
    return list(sorted(listdict, key=lambda d: d[key], reverse=reverse))


def flattern(L):
    'take a list of lists and return a list of the elements [[l]] -> [l]'
    al = []
    [al := [*al, *l] for l in L]
    return al


def seperate(*args):
    LD = args[-1]
    keys = get_keys(LD)
    l_keys = set(args[:-1]).intersection(keys)
    r_keys = keys.difference(l_keys)
    left_LD = [dict(zip(l_keys, row)) for row in zip(*get(*l_keys, LD))]
    rigt_LD = [dict(zip(r_keys, row)) for row in zip(*get(*r_keys, LD))]
    return left_LD, rigt_LD


def std(xs, mean=None):
    '''Standard Deviation of the given vector.
    sqrt(E[(X - E[X])^2]) = sqrt( Sum_i  (X_i - <X>)^2/N)
    To find the Standard Error, the variation of resampled means, dived by sqrt(N) '''
    mean = mean or average(xs)
    return sqrt(sum([(x - mean) ** 2 for x in xs]) / len(xs))


def to_table(LD, header=True):
    keys = list(set.union(*[set(D) for D in LD]))
    lengths = list_dict_map(lambda item: len(str(item)), LD)
    max_lengths = {key: max([len(key), *get(key, lengths)]) for key in keys}
    # key_lengths = {key: len(key) for key in keys}
    #  row_length = sum([L for L in key_lengths.values()]) + 3*len(keys) + 1

    class table:
        cont = []

        def __init__(self):
            self.cont.append('| ')

        def new_line(self):
            self.cont.append('\n| ')
            return self

        def add(self, item):
            self.cont.append(item + ' | ')
            return self

        def end(self):
            self.cont.append('\n')
            return ''.join(self.cont)

    table = table()

    if header:
        for key in keys:
            table.add(key.rjust(max_lengths[key]))

    for D in LD:
        table.new_line()
        for key in keys:
            table.add(str(D[key]).rjust(max_lengths[key]))

    return table.end()


def table_print(listdict, header=True):
    print(to_table(listdict, header=header))
