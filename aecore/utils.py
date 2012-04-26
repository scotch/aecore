
class dotdict(dict):
    """
    from http://parand.com/say/index.php/2008/10/24/python-dot-notation-dictionary-access/
    """
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__


def merge_dicts(default_values, user_values):
    if user_values is None:
        return default_values
    config = {}
    for k, v in user_values.items():
        if k in default_values:
            if isinstance(v, dict):
                cloned = user_values[k].copy()
                for key, value in default_values[k].items():
                    if key is not None and key not in user_values[k]\
                    or user_values[k][key] == '':
                        cloned[key] = value
                config[k] = cloned
            else:
                config[k] = v
        else:
            config[k] = v
    for k, v in default_values.items():
        if k not in config:
            config[k] = v
    return config


def import_class(full_path):
    path_split = full_path.split('.')
    path = ".".join(path_split[:-1])
    klass = path_split[-1]
    mod = __import__(path, fromlist=[klass])
    return getattr(mod, klass)


def camelcase_to_underscore(value):
    """
    http://stackoverflow.com/a/1176023/236564
    :param value:
    :return:
    """
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def underscore_to_camelcase(value):
    """
    http://stackoverflow.com/a/4306777/236564
    :param value:
    :return:
    """
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def validate_email(email):
    import re
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) is not None:
            return True
    return False

def flat_dict_to_nested_dict(d, dict_char='.', list_char='-'):
    """
    Decode the flat dictionary d into a nested structure.

    from https://bitbucket.org/formencode/official-formencode/src/06d52c5b33c9/formencode/variabledecode.py

    Takes GET/POST variable dictionary, as might be returned by ``cgi``,
    and turns them into lists and dictionaries.

    Keys (variable names) can have subkeys, with a ``.`` and
    can be numbered with ``-``, like ``a.b-3=something`` means that
    the value ``a`` is a dictionary with a key ``b``, and ``b``
    is a list, the third(-ish) element with the value ``something``.
    Numbers are used to sort, missing numbers are ignored.

    This doesn't deal with multiple keys, like in a query string of
    ``id=10&id=20``, which returns something like ``{'id': ['10', '20']}``.
    That's left to someplace else to interpret.  If you want to
    represent lists in this model, you use indexes, and the lists are
    explicitly ordered.

    If you want to change the character that determines when to split for
    a dict or list, both variable_decode and variable_encode take dict_char
    and list_char keyword args. For example, to have the GET/POST variables,
    ``a_1=something`` as a list, you would use a ``list_char='_'``.


    """
    result = {}
    dicts_to_sort = set()
    known_lengths = {}
    for key, value in d.items():
        keys = key.split(dict_char)
        new_keys = []
        was_repetition_count = False
        for key in keys:
            if key.endswith('--repetitions'):
                key = key[:-len('--repetitions')]
                new_keys.append(key)
                known_lengths[tuple(new_keys)] = int(value)
                was_repetition_count = True
                break
            elif list_char in key:
                key, index = key.split(list_char)
                new_keys.append(key)
                dicts_to_sort.add(tuple(new_keys))
                new_keys.append(int(index))
            else:
                new_keys.append(key)
        if was_repetition_count:
            continue

        place = result
        for i in range(len(new_keys)-1):
            try:
                if not isinstance(place[new_keys[i]], dict):
                    place[new_keys[i]] = {None: place[new_keys[i]]}
                place = place[new_keys[i]]
            except KeyError:
                place[new_keys[i]] = {}
                place = place[new_keys[i]]
        if new_keys[-1] in place:
            if isinstance(place[new_keys[-1]], dict):
                place[new_keys[-1]][None] = value
            elif isinstance(place[new_keys[-1]], list):
                if isinstance(value, list):
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]].append(value)
            else:
                if isinstance(value, list):
                    place[new_keys[-1]] = [place[new_keys[-1]]]
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]] = [place[new_keys[-1]], value]
        else:
            place[new_keys[-1]] = value

    try:
        to_sort_list = sorted(dicts_to_sort, key=len, reverse=True)
    except NameError: # Python < 2.4
        to_sort_list = list(dicts_to_sort)
        to_sort_list.sort(lambda a, b: -cmp(len(a), len(b)))
    for key in to_sort_list:
        to_sort = result
        source = None
        last_key = None
        for sub_key in key:
            source = to_sort
            last_key = sub_key
            to_sort = to_sort[sub_key]
        if None in to_sort:
            noneVals = [(0, x) for x in to_sort.pop(None)]
            noneVals.extend(to_sort.items())
            to_sort = noneVals
        else:
            to_sort = to_sort.items()
        to_sort.sort()
        to_sort = [v for k, v in to_sort]
        if key in known_lengths:
            if len(to_sort) < known_lengths[key]:
                to_sort.extend(['']*(known_lengths[key] - len(to_sort)))
        source[last_key] = to_sort

    return result

