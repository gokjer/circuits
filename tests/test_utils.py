import pytest

from utils import incrementing_dict, encouple


def test_incrementing_dict():
    d = incrementing_dict()
    assert d[1] + d[2] + d[8] == 6
    assert d[1] == 1
    assert d[2] == 2
    assert d[8] == 3


def test_incrementing_dict_setitem():
    d = incrementing_dict()
    with pytest.raises(RuntimeError):
        d[1] = 2


def test_encouple():
    inp = (1, 2, 3, 4)
    assert list(encouple(inp)) == [(1, 2), (2, 3), (3, 4)]
    assert list(encouple([])) == []
