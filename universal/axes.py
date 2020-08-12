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

    def __lt__(self, other):
        assert isinstance(other, Axis), 'can only compare an axis to an axis'
        return self.count < other.count


class Axes:
    def __init__(self, axes=None):
        self.axes = tuple(sorted(axes or ()))

    def __iter__(self):
        for values in product([False, True], repeat=len(self.axes)):
            elem = Coordinates()
            elem.update(zip(self.axes, values))
            yield elem

    def __eq__(self, other):
        return self.axes == other.axes


def closure(*axes_instances):
    axes = set()
    for instance in axes_instances:
        axes.update(instance.axes)
    return Axes(axes=axes)


class Coordinates(UserDict):
    def project(self, axes: Axes):
        assert all(axis in self.data for axis in axes.axes), \
            f'Cannot project coordinates on {self.data.keys()} on {axes.axes}'
        result = Coordinates()
        result.update(((axis, self.data[axis]) for axis in axes.axes))
        return result

    def int_value(self):
        result = 0
        base = 1
        # dict is supposed to be sorted, so the `sorted` is just a precaution here
        for _, val in sorted(self.items()):
            result += int(val) * base
            base *= 2
        return result
