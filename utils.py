from collections import defaultdict


class incrementing_dict(defaultdict):
    def __init__(self, *args, start_count=1, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = start_count

    def __missing__(self, key):
        super().__setitem__(key, self._count)
        self._count += 1
        return self[key]

    def __setitem__(self, key, value):
        raise RuntimeError('Direct insertion is forbidden for incrementing dict')


def test_incrementing_dict():
    d = incrementing_dict()
    assert d[1] + d[2] + d[8] == 6
    assert d[1] == 1
    assert d[2] == 2
    assert d[8] == 3
    # TODO assert setitem raises an error
