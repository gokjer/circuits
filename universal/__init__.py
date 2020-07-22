from collections import defaultdict

from universal.axes import closure
from universal.renderable import Renderable, RenderableObject
from universal.variables import Variable


class Array(RenderableObject):
    name = 'array'
    variable_cls = Variable

    def __init__(self, size, origin=None, origin_inputs=None, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        if origin is not None:
            assert isinstance(origin, RenderableMapping), 'Origin must be either a mapping or None'
        else:
            assert not self.dependencies, 'Cannot have dependencies without an origin'
        self.origin = origin
        self.origin_inputs = origin_inputs
        self.variables = [self.variable_cls(array=self, dependencies=[self]) for _ in range(self.size)]

    def __getitem__(self, item):
        return self.variables[item]

    def pre_render(self, engine, **kwargs):
        super().pre_render(engine, **kwargs)
        if self.origin and not engine.is_rendered(self.origin):
            self.origin.render(engine, **kwargs)

    def do_render(self, engine, **kwargs):
        engine.render_array(self, **kwargs)

    def __str__(self):
        return f'[{self.origin and str(self.origin) or ""}]_{super().__str__()}'

    def is_free(self):
        assert self.origin is not None or not self.dependencies, 'Cannot have dependencies without an origin'
        return self.origin is None


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


class Function(RenderableMapping):
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

    def do_render(self, engine, **kwargs):
        engine.render_function(self, **kwargs)


class ChoiceMapping(RenderableMapping):
    name = 'choice_map'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, output_degree=2)

    def do_render(self, engine, **kwargs):
        engine.render_choice_mapping(self, **kwargs)


class Condition(Renderable):
    def __init__(self, variables):
        super().__init__()
        self.variables = variables


class Equality(Condition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for var1, var2 in zip(self.variables, self.variables[1:]):
            assert var1.axes == var2.axes, 'Variables {var1} and {var2} are not comparable'

    def do_render(self, engine, **kwargs):
        engine.render_equality(self, **kwargs)


class Engine:
    def __init__(self):
        self.rendered = set()  # {variable_id}

    def is_rendered(self, elem):
        return str(elem) in self.rendered

    def mark_rendered(self, elem: Renderable):
        self.rendered.add(str(elem))

    def render_variable(self, variable: Variable, **kwargs):
        if variable.is_free():
            self.render_free_variable(variable, **kwargs)
        else:
            self.render_bound_variable(variable, **kwargs)

    def render_free_variable(self, variable: Variable, **kwargs):
        raise NotImplementedError

    def render_bound_variable(self, variable: Variable, **kwargs):
        raise NotImplementedError

    def render_array(self, array: Array, **kwargs):
        if array.is_free():
            self.render_free_array(array, **kwargs)
        else:
            self.render_bound_array(array, **kwargs)

    def render_free_array(self, array: Array, **kwargs):
        for var in array.variables:
            var.render(self, ignore_dependencies=True)
        self.mark_rendered(array)

    def render_bound_array(self, array: Array, **kwargs):
        if isinstance(array.origin, Function):
            self.render_function_output(array, **kwargs)
        elif isinstance(array.origin, ChoiceMapping):
            self.render_choice_output(array, **kwargs)
        else:
            raise TypeError(f'Unknown origin type {type(array.origin)}')

    def render_function_output(self, array: Array, **kwargs):
        raise NotImplementedError

    def render_choice_output(self, array: Array, **kwargs):
        raise NotImplementedError

    def render_function(self, function: Function, **kwargs):
        raise NotImplementedError

    def render_choice_mapping(self, choice_map: ChoiceMapping, **kwargs):
        raise NotImplementedError

    def render_equality(self, equality: Equality, **kwargs):
        for var1, var2 in zip(equality.variables, equality.variables[1:]):
            self.set_equal(var1, var2, **kwargs)

    def set_equal(self, variable1: Variable, variable2: Variable, **kwargs):
        raise NotImplementedError
