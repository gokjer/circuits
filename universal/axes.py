from collections import UserDict
from itertools import product

from utils import InstanceCounterMeta


class Axis(metaclass=InstanceCounterMeta):
    def __init__(self):
        self.count = next(self.__class__.counter)

    def __hash__(self):
        return self.count

    def __str__(self):
        return f'axis_{self.count}'


class Axes:
    def __init__(self, axes=None):
        self.axes = tuple(sorted(axes or ()))

    def __iter__(self):
        for values in product([False, True], repeat=len(self.axes)):
            coords = dict(zip(self.axes, values))
            yield Coordinates(**coords)


def closure(*axes_instances):
    axes = set()
    for instance in axes_instances:
        axes.update(instance.axes)
    return Axes(axes=axes)


class Coordinates(UserDict):
    def project(self, axes: Axes):
        assert all(axis in self.data for axis in axes.axes), \
            f'Cannot project coordinates on {self.data.keys()} on {axes.axes}'
        new_data = {axis: self.data[axis] for axis in axes.axes}
        return Coordinates(**new_data)
