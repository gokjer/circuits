from collections import defaultdict

from universal.axes import closure
from universal.renderable import Renderable, RenderableObject
from universal.variable import Variable


class Array(RenderableObject):
    name = 'array'
    variable_cls = Variable

    def __init__(self, size, origin, origin_inputs=None, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        assert isinstance(origin, RenderableMapping), 'Origin must be a mapping'
        self.origin = origin
        self.origin_inputs = origin_inputs
        self.variables = [self.variable_cls(array=self) for _ in range(self.size)]

    def __getitem__(self, item):
        return self.variables[item]

    def pre_render(self, renderer, **kwargs):
        super().pre_render(renderer, **kwargs)
        if self.origin and not renderer.is_rendered(self.origin):
            self.origin.render(renderer, **kwargs)

    def do_render(self, renderer, **kwargs):
        renderer.render_array(self, **kwargs)

    def __str__(self):
        return f'[{self.origin and str(self.origin) or ""}]_{super().__str__()}'


class RenderableMapping(Renderable):
    name = 'mapping'
    array_cls = Array

    def __init__(self, input_degree, output_degree):
        super().__init__()
        self.input_degree = input_degree
        self.output_degree = output_degree

    def __call__(self, input_vars, **kwargs):
        assert len(input_vars) == self.input_degree, f'Wrong input size: {len(input_vars)} instead of {self.input_degree}'
        outputs = self.array_cls(size=self.output_degree, dependencies=input_vars, origin=self, origin_inputs=input_vars)
        return outputs


class FunctionMapping(RenderableMapping):
    POSSIBLE_VALUES = [False, True]
    name = 'function'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.values = defaultdict(dict)

    def set_value(self, input_values, output_index, output_value):
        assert 0 <= output_index < self.output_degree, f'output_index is {output_index}, must be in [0, {self.output_degree})'
        assert len(input_values) == self.input_degree, f'Wrong input size: {len(input_values)} instead of {self.input_degree}'
        assert all([value in self.POSSIBLE_VALUES for value in input_values]), f'All input values must be one of {self.POSSIBLE_VALUES}'
        assert output_value in self.POSSIBLE_VALUES, f'Output value is {output_value}, must be one of {self.POSSIBLE_VALUES}'
        assert output_index not in self.values[input_values], f'Output index {output_index} is already set for values {input_values}'
        self.values[output_index][tuple(input_values)] = output_value

    def do_render(self, renderer, **kwargs):
        renderer.render_function_mapping(self, **kwargs)


class ChoiceMapping(RenderableMapping):
    name = 'choice_map'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('output_degree', 2)
        super().__init__(*args, **kwargs)

    def do_render(self, renderer, **kwargs):
        renderer.render_choice_mapping(self, **kwargs)


class Condition(Renderable):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables


class Equality(Condition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for var1, var2 in zip(self.variables, self.variables[1:]):
            assert var1.axes == var2.axes, 'Variables {var1} and {var2} are not comparable'

    def do_render(self, renderer, **kwargs):
        renderer.render_equality(self, **kwargs)
