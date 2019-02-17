import re
import os

FIELD_SEP = "__"
TABLE_SEP = "____"

is_str = lambda stru: isinstance(stru, str)
is_int = lambda stru: isinstance(stru, int)
is_bool = lambda stru: isinstance(stru, bool)
is_float = lambda stru: isinstance(stru, float)
is_list = lambda stru: isinstance(stru, list)
is_dict = lambda stru: isinstance(stru, dict)
is_base = lambda stru: any((f(stru) for f in (is_str, is_int, is_bool, is_float)))
is_stru = lambda stru: any((f(stru) for f in (is_base, is_list, is_dict)))

stru_type = lambda stru: type(stru).__name__
clean_string = lambda string: re.sub(r"[^ _a-zA-Z0-9]", "", string)


def linearize(table_name, structura):
    for output in linearize__deconstruct(
            table=table_name,
            stru=linearize__simplify(structura),
            ids=None):
        yield output


def linearize__simplify(stru):
    if is_base(stru):
        return stru
    if is_list(stru):
        return list(map(linearize__simplify, filter(is_stru, stru)))
    if is_dict(stru):
        new_stru = dict()
        for key, val in stru.items():
            if is_dict(val):
                for nkey, nval in val.items():
                    if is_stru(nval):
                        nkey_name = \
                            f"{clean_string(key)}{FIELD_SEP}{clean_string(nkey)}"
                        new_stru[nkey_name] = nval
                new_stru = linearize__simplify(new_stru)
            elif is_stru(val):
                new_stru[clean_string(key)] = linearize__simplify(val)
        return new_stru
    return None


def linearize__deconstruct(table, stru, ids):
    if is_base(stru):
        ids = [] if ids is None else ids
        for output in linearize__deconstruct(
                table=table, stru=[stru], ids=ids):
            yield output
    elif is_list(stru):
        for nstru in stru:
            mstru = nstru if is_dict(nstru) else {"val": nstru}
            for lvl, this_id in enumerate(ids):
                mstru[f"sid{lvl}"] = this_id
            for output in linearize__deconstruct(
                    table=table, stru=mstru, ids=ids):
                yield output
    elif is_dict(stru):
        record = {}
        for nkey, nstru in stru.items():
            if is_base(nstru):
                record[nkey] = nstru
            elif is_list(nstru):
                nid = os.urandom(64).hex()
                ntable = f"{table}{TABLE_SEP}{nkey}"
                ntable_ids = [nid] if ids is None else ids + [nid]
                record[ntable] = nid
                for output in linearize__deconstruct(
                        table=ntable, stru=nstru, ids=ntable_ids):
                    yield output
        yield (table, record)
