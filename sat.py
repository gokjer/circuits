from collections import defaultdict

from universal import Engine
from utils import incrementing_dict


class SATEngine(Engine):
    def __init__(self):
        self.clauses = []
        self.symbols = incrementing_dict()
        self.vars = defaultdict(list)
        self.functions = defaultdict(list)
        self.choices = defaultdict(list)
        self.rendered = set()

    def is_rendered(self, elem):
        return str(elem) in self.rendered

    def render_basic_variable(self, variable, **kwargs):
        var_id = str(variable)
        self.vars[var_id] = [f'{var_id}_{i}' for i in range(2)]
        # TODO set to true/false
        self.rendered.add(var_id)

    def render_complex_variable(self, variable, **kwargs):
        pass

    def render_function(self, function, **kwargs):
        pass

    def render_choice_mapping(self, choice, **kwargs):
        pass
