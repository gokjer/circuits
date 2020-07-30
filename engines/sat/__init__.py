from collections import defaultdict
from itertools import product, combinations

from engines.sat.logical import exactly_one, set_value, equal_symbols
from universal import Array, Function, ChoiceMapping, Variable, closure
from universal.engine import Engine
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
        self.frameset = {}

    def render_free_variable(self, variable, **kwargs):
        var_id = str(variable)
        self.vars[var_id] = [f'{var_id}_{i}' for i in range(2)]
        for symbol, val in zip(self.vars[var_id], [False, True]):
            self.clauses.append(set_value(symbol, val))
        self.mark_rendered(variable)

    def render_bound_variable(self, variable, **kwargs):
        self.mark_rendered(variable)

    def render_function_output(self, array: Array, **kwargs):
        # TODO
        pass

    def render_choice_output(self, array: Array, **kwargs):
        assert isinstance(array.origin, ChoiceMapping), \
            f'Trying to render choice output while origin is not a ChoiceMapping, but a {type(array.origin)}'
        variable1, variable2 = array.variables
        assert variable1.axes == variable2.axes, 'Choice output variables must have the same axes'
        choice_id = str(array.origin)
        for comb, symb in zip(combinations(array.origin_inputs, 2), self.choices[choice_id]):
            input1, input2 = comb
        # TODO
        self.mark_rendered(variable1)
        self.mark_rendered(variable2)

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

    def set_equal(self, variable1: Variable, variable2: Variable, **kwargs):
        pass

    def equal_vars(self, variable1: Variable, variable2: Variable):
        axes = closure(variable1.axes, variable2.axes)
        for coord in axes:
            pass
        # TODO
