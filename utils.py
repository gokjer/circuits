from collections import defaultdict
from contextlib import contextmanager
from itertools import count, product
from time import perf_counter


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


def all_inputs(dim: int):
    yield from product([False, True], repeat=dim)


def print_dependency_tree(var, offset=0, step=2):
    print(' ' * offset, var)
    for dep in var.dependencies or []:
        print_dependency_tree(dep, offset=offset+step, step=step)


@contextmanager
def time_and_log(process_name):
    start_time = perf_counter()
    try:
        yield
    finally:
        print(f'{process_name} finished in {perf_counter() - start_time} seconds')
