from collections import defaultdict
from itertools import product

from conditions import exactly_one, set_value
from universal import Engine, Array, Variable, Function, ChoiceMapping, Renderable
from utils import incrementing_dict


def all_inputs(dim: int):
    yield from product([False, True], repeat=dim)


class SATEngine(Engine):
    def __init__(self):
        super().__init__()
        self.clauses = []  # [[+-symbol_id]]
        self.symbols = incrementing_dict()  # symbol -> symbol_id
        self.vars = defaultdict(list)  # variable_id -> [symbol]
        self.functions = defaultdict(lambda: defaultdict(list))  # function_id -> (out_index -> [symbol])
        self.choices = defaultdict(list)  # choice_id -> [symbol]
        self.rendered = set()  # {variable_id}
        self.frameset = {}

    def is_rendered(self, elem):
        return str(elem) in self.rendered

    def mark_rendered(self, elem: Renderable):
        self.rendered.add(str(elem))

    def render_free_variable(self, variable, **kwargs):
        var_id = str(variable)
        self.vars[var_id] = [f'{var_id}_{i}' for i in range(2)]
        for symbol, val in zip(self.vars[var_id], [False, True]):
            self.clauses.append(set_value(symbol, val))
        self.mark_rendered(variable)

    def render_bound_variable(self, variable, **kwargs):
        self.mark_rendered(variable)

    def render_function_output(self, array: Array, **kwargs):
        pass

    def render_choice_output(self, array: Array, **kwargs):
        pass

    def render_function(self, function: Function, **kwargs):
        fun_id = str(function)
        for out_ind in range(function.output_degree):
            for input_id, input in enumerate(all_inputs(function.input_degree)):
                symbol = f'{fun_id}_{out_ind}_{input_id}'
                self.functions[fun_id][out_ind].append(symbol)
                symbol_id = self.symbols[symbol]
                if input in function.values[out_ind]:
                    self.clauses.append(set_value(symbol_id, function.values[out_ind][input]))
        self.mark_rendered(function)

    def render_choice_mapping(self, choice: ChoiceMapping, **kwargs):
        choice_id = str(choice)
        for i in range(choice.input_degree - 1):
            for j in range(i+1, choice.input_degree):
                self.choices[choice_id].append(f'{choice_id}_{i}_{j}')
        self.clauses.extend(
            exactly_one([self.symbols[symbol] for symbol in self.choices[choice_id]])
        )
        self.mark_rendered(choice)
