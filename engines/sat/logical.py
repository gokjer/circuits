from itertools import combinations


def exactly_one(symb_ids):
    result = [symb_ids]
    for u, v in combinations(symb_ids, 2):
        result.append([-u, -v])
    return result


def equals_value(symb, val: bool):
    if val:
        return [symb]
    return [-symb]


def if_then(all_true, then):
    negated = [-symbol for symbol in all_true]
    return [negated + clause for clause in then]


def equal_symbols(symb1, symb2):
    return [[symb1, -symb2], [-symb1, symb2]]
