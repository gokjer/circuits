from utils import InstanceCounterMeta
from universal.axes import closure, Axes


class Renderable(metaclass=InstanceCounterMeta):
    name = 'base'

    def __init__(self):
        self.count = next(self.__class__.counter)

    def pre_render(self, engine, **kwargs):
        assert not engine.is_rendered(self), f'{self} is already rendered'

    def do_render(self, engine, **kwargs):
        raise NotImplementedError

    def post_render(self, engine, **kwargs):
        pass

    def render(self, engine, **kwargs):
        self.pre_render(engine, **kwargs)
        self.do_render(engine, **kwargs)
        self.post_render(engine, **kwargs)

    def __str__(self):
        return f'{self.name}_{self.count}'


class RenderableObject(Renderable):
    name = 'object'

    def __init__(self, dependencies=None, name=None):
        super().__init__()
        self.dependencies = dependencies or []
        self.name = name or self.name
        self._axes = None

    @property
    def axes(self) -> Axes:
        if self._axes is None:
            if self.dependencies:
                self._axes = closure(dep.axes for dep in self.dependencies)
            else:
                self._axes = self.new_axes()
        return self._axes

    @staticmethod
    def new_axes():
        raise NotImplementedError

    def pre_render(self, engine, ignore_dependencies=False, **kwargs):
        super().pre_render(engine, **kwargs)
        if not ignore_dependencies:
            for dep in self.dependencies:
                if not engine.is_rendered(dep):
                    dep.render(engine, **kwargs)
