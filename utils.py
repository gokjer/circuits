from collections import defaultdict
from itertools import count


# noinspection PyPep8Naming
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
        # TODO add more suitable error here
        raise RuntimeError('Direct insertion is forbidden for incrementing dict')


class InstanceCounterMeta(type):
    """
    Metaclass to make instance counter not share count with descendants
    (c) https://stackoverflow.com/questions/8628123/counting-instances-of-a-class
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.counter = count(0)


def encouple(iterable):
    """
    [1, 2, 3, 4] -> (1, 2), (2, 3), (3, 4)
    """
    memory = list(iterable)
    return zip(memory, memory[1:])
