from collections import defaultdict


class incrementing_dict(defaultdict):
    def __init__(self, start_count=1, **kwargs):
        assert 'default_factory' not in kwargs, 'Cannot use default_factory'
        super().__init__(**kwargs)
        self._count = start_count

    def __missing__(self, key):
        super().__setitem__(key, self._count)
        self._count += 1
        return self[key]

    def __setitem__(self, key, value):
        raise RuntimeError('Direct insertion is forbidden for incrementing dict')
