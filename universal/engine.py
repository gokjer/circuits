from universal import Renderable, Variable, Array, Function, ChoiceMapping, Equality


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
