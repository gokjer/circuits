from collections import defaultdict

from utils import InstanceCounterMeta


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

    def pre_render(self, engine, ignore_dependencies=False, **kwargs):
        super().pre_render(engine, **kwargs)
        if not ignore_dependencies:
            for dep in self.dependencies:
                if not engine.is_rendered(dep):
                    dep.render(engine, **kwargs)


class Variable(RenderableObject):
    name = 'variable'

    def __init__(self, array=None, **kwargs):
        super().__init__(**kwargs)
        self.array = array
    #     self.base_dependencies = None
    #
    # def get_base_deps(self):
    #     if self.base_dependencies is None:
    #         result = {}
    #         for dep in self.dependencies:
    #             result.update(dep.get_base_deps())
    #         if not result:
    #             result = {self}
    #         self.base_dependencies = frozenset(result)
    #     return self.base_dependencies

    def do_render(self, engine, **kwargs):
        engine.render_variable(self, **kwargs)

    def __str__(self):
        return f'{self.array and str(self.array) or ""}_{super().__str__()}'

    def is_free(self):
        return self.array is None or self.array.is_free()


class Array(RenderableObject):
    name = 'array'
    variable_cls = Variable

    def __init__(self, size, origin=None, **kwargs):
        super().__init__(**kwargs)
        self.size = size
        if origin is not None:
            assert isinstance(origin, RenderableMapping), 'Origin must be either a mapping or None'
        self.origin = origin
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
        return self.origin is None and not self.dependencies


class RenderableMapping(Renderable):
    name = 'mapping'
    array_cls = Array

    def __init__(self, input_degree, output_degree):
        super().__init__()
        self.input_degree = input_degree
        self.output_degree = output_degree

    def __call__(self, input_vars, **kwargs):
        assert len(input_vars) == self.input_degree, f'Wrong input size: {len(input_vars)} instead of {self.input_degree}'
        outputs = self.array_cls(size=self.output_degree, dependencies=input_vars, origin=self)
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


class Engine:
    def __init__(self):
        self.rendered = set()  # {variable_id}
        self.frameset = {}

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
