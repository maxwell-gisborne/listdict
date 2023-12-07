def by(key, L):
    d = {}
    for l in L:
        if not l[key] in d:
            d[l[key]] = []
        d[l[key]].append(l)
    return d

def get(*args):
    L = args[-1]
    keys = args[:-1]
    get_lambda = lambda key: list(map(lambda l: l[key], L))
    if len(keys) == 0:
        key = L
        return lambda L: list(map(lambda l: l[key], L))
    if len(keys) == 1:
        key = keys[0]
        return get_lambda(key)
    else:
        return [get_lambda(key) for key in keys]

def get_keys(LD):
    return set.union(*[set(D) for D in LD])

def hermoginise(ld: [dict()], default=None):
    keys = get_keys(ld)
    new_ld = []
    for d in ld:
        new_ld.append({k:(d.get(k) or default) for k in keys})
    return new_ld

def split_by_quote(string: str):
    parts = []
    class Mode:
        normal = 0
        quote = 1
        escape = 2
        brackets = 3
    brackets = {'[':']', '{':'}', '(':')', '<':'>'}
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

scope = [None]
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

def to_csv(LD: [dict]) -> str :
    keys = get_keys(LD)
    body = []
    for D in LD:
        body.append(',\t'.join([(str(D[k]) or '') for k in keys]))
    return ',\t'.join(keys) + '\n' + ',\t'.join(body)

def dict_map(foo,D):
    'map a function over the values of a dictionary'
    return {key:foo(value) for key,value in D.items()}

def list_dict_map(foo,LD):
    'map a function over the values of the dictionaries in a listdict'
    return list(map(lambda D: dict_map(foo,D),LD))

def transform(foodict,LD):
    '''Transfor a listdict by updateing the values of the constituant dictionaries in acordence with the function dictionary passed.
      { key:function }, [{ key:value }] => [{ key:function(value) }]'''
    if callable(foodict):
        foo = foodict
        foodict = {k: foo for k in get_keys(LD)}
    def update_dict(D):
        for key,foo in foodict.items():
            D = ( D | { key:foo( D[key] ) } ) if key in D else D
        return D
    return list(map(update_dict,LD)) if LD else update_dict

def join(*listdicts):
    agragate_listdict = []
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
    with open(filename,'r') as f:
        return yaml.load(f,yaml.loader.SafeLoader)

def average(xs):
    'finds the mean of the input list'
    return sum(xs)/len(xs)

def sort_list_dict(key,listdict,reverse=False):
    return list(sorted(listdict,key=lambda d: d[key],reverse=reverse))

def flattern(L):
    'take a list of lists and return a list of the elements [[l]] -> [l]'
    al = []
    [al := [*al, *l] for l in L]
    return al

def seperate(*args):
    listdict = args[-1]
    keys = get_keys(listdict)
    l_keys = set(args[:-1]).intersection(keys)
    r_keys = keys.difference(l_keys)
    
    l_listdict = [ dict(zip(l_keys, row)) for row in zip(*get(*l_keys,listdict)) ]
    r_listdict = [ dict(zip(r_keys, row)) for row in zip(*get(*r_keys,listdict)) ]
    
    return l_listdict, r_listdict
    


def std(xs,mean=None):
    '''Standard Deviation of the given vector. 
    sqrt(E[(X - E[X])^2]) = sqrt( Sum_i  (X_i - <X>)^2/N) 
    To find the Standard Error, the variation of resampled means, dived by sqrt(N) '''
    mean = mean or average(xs)
    return sqrt(sum([(x - mean) ** 2 for x in xs]) / len(xs))

from math import sqrt

def table_format(listdict,header=True):
    keys = list(set.union(*[set(d) for d in listdict]))
    lengths = list_dict_map(lambda item: len(str(item)),listdict)
    max_lengths = {key: max([len(key), *get(key,lengths)]) for key in keys }
    key_lengths = {key:len(key) for key in keys}
    row_length = sum([l for l in key_lengths.values()]) + 3*len(keys) + 1

    table = []
    start    = lambda      : table.append('| ')
    new_line = lambda      : table.append('\n| ')
    add      = lambda item : table.append(item + ' | ')
    end      = lambda      : table.append('\n')
    
    start()

    if header:
        for key in keys:
            add(key.rjust(max_lengths[key]))
  
    for d in listdict:
        new_line()
        for key in keys:
            add(str(d[key]).rjust(max_lengths[key]))

    end()
    return ''.join(table)

def table_print(listdict,header=True):
    print(table_format(listdict,header=header))

class Table(list):
    def __repr__(self):
        return table_format(self)

    def map(self,*foos):
        data = list(self)
        for foo in foos:
            data = list_dict_map(foo)
        return Table(data)

    def transform(self,**foodict):
        return Table(transform(foodict,list(self)))

    def get(self,*args):
        return get(*args,list(self))

    def by(self,key):
        return dict_map(Table, by(key,list(self)))

    def join(self,**colum_dicts):
        others = [ [{key:value} for value in values] for key,values in colum_dicts.items() ]
        return Table(join(*map(list,[self,*others])))

    def scatter(self,key1,key2,by=None,scatter_args={},fig_ax=None):
        import matplotlib.pyplot as plt
        fig,ax = fig_ax or plt.subplots()
        ax.grid()
        if by == None:
            ax.scatter(*self.get(key1,key2),**scatter_args)
        else:
            for label,data in self.by(by).items():
                ax.scatter(*data.get(key1,key2),label=f'{by} = {label}',**scatter_args)
        ax.legend()
        return fig,ax
        
    def sort(self,key,reverse=False):
        return Table(sort_list_dict(key,list(self),reverse=reverse))

    def seperate(self,*keys):
        l,r = seperate(*keys,list(self))
        return Table(l),Table(r)

import inspect
class Scope:
    """
    A context manager that binds keys and values from a dictionary to
    variable names within the scope of a `with` statement.

    The variable bindings are cleaned up and the dictionary is updated
    with any changes made to the variables when the `with` block is exited.

    Usage:
        my_dict = {"x": 10, "y": 20, "z": 30}
        with Scope(my_dict):
            print(x, y, z)  # Output: 10 20 30
            x = 15
        print(my_dict)  # Output: {'x': 15, 'y': 20, 'z': 30}
    """

    def __init__(self, bindings):
        self.bindings = bindings
        self.original_globals = {}

    def __enter__(self):
        frame = inspect.currentframe()
        try:
            self.caller_globals = frame.f_back.f_globals
        finally:
            # Clean up the reference to the frame to avoid reference cycles
            del frame

        for key, value in self.bindings.items():
            if key in self.caller_globals:
                self.original_globals[key] = self.caller_globals[key]
            self.caller_globals[key] = value


    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.bindings.keys():
            # Update the bindings with the current value of the variables
            self.bindings[key] = self.caller_globals[key]

            if key in self.original_globals:
                self.caller_globals[key] = self.original_globals[key]
            else:
                del self.caller_globals[key]
