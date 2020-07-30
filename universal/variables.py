from universal.renderable import RenderableObject
from universal.axes import Axes, Axis


class Variable(RenderableObject):
    name = 'variable'

    def __init__(self, array=None, **kwargs):
        super().__init__(**kwargs)
        self.array = array
        if self.array and self.array not in self.dependencies:
            self.dependencies.append(self.array)
        self._axes = None

    @staticmethod
    def new_axes():
        return Axes(axes=[Axis()])

    def do_render(self, engine, **kwargs):
        engine.render_variable(self, **kwargs)

    def __str__(self):
        return f'{self.array and str(self.array) or ""}_{super().__str__()}'

    def is_free(self):
        return self.array is None
