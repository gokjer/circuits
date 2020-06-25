from ..utils import incrementing_dict


def test_incrementing_dict():
    d = incrementing_dict()
    assert d[1] + d[2] + d[8] == 6
    assert d[1] == 1
    assert d[2] == 2
    assert d[8] == 3
    # TODO assert setitem raises an error
