from collections import UserDict

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
        self.axes = set(axes or ())


def closure(*axes_instances):
    axes = set()
    for instance in axes_instances:
        axes |= instance.axes
    return Axes(axes=axes)


class Coordinates(UserDict):
    def project(self, axes: Axes):
        assert all(axis in self.data for axis in axes.axes), \
            f'Cannot project coordinates on {self.data.keys()} on {axes.axes}'
        new_data = {axis: self.data[axis] for axis in axes.axes}
        return Coordinates(**new_data)
