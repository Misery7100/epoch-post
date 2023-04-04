import yaml

# ----------------------------- #

UNIT_TRANSFORM = {
    'zepto' : 1e-21,
    'atto' : 1e-18,
    'femto' : 1e-15,
    'pico' : 1e-12,
    'nano' : 1e-9,
    'micro' : 1e-6,
    'milli' : 1e-3,
    'centi' : 1e-2,
    'kilo' : 1e3,
    'mega' : 1e6,
    'giga' : 1e9,
    'tera' : 1e12,
    'peta' : 1e15
}

UNIT_SHORT = {
    'nano' : r'$\rm{nm}$',
    'micro' : r'$\rm{\mu m}$'
}

VECTOR_TO_NAME = {
    'E' : 'Electric_Field',
    'B' : 'Magnetic_Field',
    'J' : 'Current'
}

VECTOR_TO_UNITS = {
    'E' : r'$V\:/\:m$',
    'B' : r'$GGs$'
}

# ----------------------------- #

class DotDict(dict):
    """Dot notation access to dictionary elements"""
    
    def __getattr__(self, attr, *args):
        if attr.startswith('__'):
            raise AttributeError
            
        val = dict.get(self, attr, *args)
        return DotDict(val) if type(val) is dict else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# ----------------------------- #

def read_yaml(path: str) -> DotDict:
    with open(path, 'r') as stream:
        f = yaml.safe_load(stream)
    
    f = DotDict(f)

    return f