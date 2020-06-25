from collections import defaultdict
from itertools import count


class InstanceCounterMeta(type):
    """
    Metaclass to make instance counter not share count with descendants
    (c) https://stackoverflow.com/questions/8628123/counting-instances-of-a-class
    """
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.counter = count(0)


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


class Variable(Renderable):
    name = 'variable'

    def __init__(self, dependencies=None, origin=None, name=None, **origin_context):
        super().__init__()
        self.dependencies = dependencies or []
        self.name = name or self.name
        self.origin = origin
        self.origin_context = origin_context
        self.base_dependencies = None

    def get_base_deps(self):
        if self.base_dependencies is None:
            result = {}
            for dep in self.dependencies:
                result.update(dep.ge_base_deps())
            if not result:
                result = {self}
            self.base_dependencies = frozenset(result)
        return self.base_dependencies

    def pre_render(self, engine, **kwargs):
        super().pre_render(engine, **kwargs)
        for dep in self.dependencies:
            if not engine.is_rendered(dep):
                dep.render(engine, **kwargs)
        if self.origin and not engine.is_rendered(self.origin):
            self.origin.render(engine, **kwargs)

    def do_render(self, engine, **kwargs):
        engine.render_variable(self, **kwargs)

    def __str__(self):
        return f'[{self.origin and self.origin.name or ""}]_{super().__str__()}'


class Mapping(Renderable):
    name = 'mapping'

    def __init__(self, input_degree, output_degree):
        super().__init__()
        self.input_degree = input_degree
        self.output_degree = output_degree

    def __call__(self, input_vars, **kwargs):
        assert len(input_vars) == self.input_degree, f'Wrong input size: {len(input_vars)} instead of {self.input_degree}'
        outputs = []
        for output_index in range(self.output_degree):
            out = Variable(dependencies=input_vars, origin=self, output_index=output_index, origin_name=self.name)
            outputs.append(out)
        return outputs


class Function(Mapping):
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
        self.values[input_values][output_index] = output_value

    def do_render(self, engine, **kwargs):
        engine.render_function(self, **kwargs)


class ChoiceMapping(Mapping):
    name = 'choice_map'

    def do_render(self, engine, **kwargs):
        engine.render_choice_mapping(self, **kwargs)


class Engine:
    def is_rendered(self, elem):
        raise NotImplementedError

    def render_variable(self, variable, **kwargs):
        if variable.origin is None:
            self.render_basic_variable(variable, **kwargs)
        else:
            self.render_complex_variable(variable, **kwargs)

    def render_basic_variable(self, variable, **kwargs):
        raise NotImplementedError

    def render_complex_variable(self, variable, **kwargs):
        raise NotImplementedError

    def render_function(self, function, **kwargs):
        raise NotImplementedError

    def render_choice_mapping(self, choice_map, **kwargs):
        raise NotImplementedError
