from collections import defaultdict
from itertools import product, combinations

from engines.sat.logical import exactly_one, equals_value, equal_symbols, if_then
from universal import Array, FunctionMapping, ChoiceMapping, Variable, closure
from universal.engine import Engine
from utils import incrementing_dict, encouple


def all_inputs(dim: int):
    yield from product([False, True], repeat=dim)


class SATEngine(Engine):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clauses = []  # [[+-symbol_id]]
        self.symbols = incrementing_dict()  # symbol -> symbol_id
        self.vars = defaultdict(list)  # variable_id -> [symbol]
        self.functions = defaultdict(lambda: defaultdict(list))  # function_id -> (out_index -> [symbol])
        self.choices = defaultdict(list)  # choice_id -> [symbol]

    def init_variable(self, variable):
        size = 2 ** len(variable.axes.axes)
        variable_id = str(variable)
        symbols = [f'{variable_id}_{i}' for i in range(size)]
        self.vars[variable_id] = symbols

    def render_free_variable(self, variable, **kwargs):
        self.init_variable(variable)
        var_id = str(variable)
        for symbol, val in zip(self.vars[var_id], [False, True]):
            self.clauses.append(equals_value(self.symbols[symbol], val))
        self.mark_rendered(variable)

    def render_bound_variable(self, variable, **kwargs):
        # TODO something?
        assert False
        self.init_variable(variable)
        self.mark_rendered(variable)

    def render_function_output(self, array: Array, **kwargs):
        """
        For each output index, the following happens:

        for each coord of output variable `var` and for each s1..sn from {True, False} (n == input_degree) we have
        (i1 == s1) & (i2 == s2) & .. & (in == sn)  =>  (var == f(s1..sn)), which we rewrite as
        (i1 != s1) | (i2 != s2) | .. | (in != sn) | (var == f(s1..sn)), where (var == f(s1..sn)) is the `statement` and
        the rest is the precondition
        """
        self._check_output_correctness(array, FunctionMapping, 'function output')
        self._init_array(array)
        fun_id = str(array.origin)
        for var, ind in zip(array.variables, range(array.origin.output_degree)):
            fun_symbs = self.functions[fun_id][ind]
            for coord in var.axes:
                out_symb = self.vars[str(var)][coord.int_value()]
                for input_values, fun_symb in zip(all_inputs(dim=array.origin.input_degree), fun_symbs):
                    statement = equal_symbols(self.symbols[out_symb], self.symbols[fun_symb])
                    precondition = []
                    for input_var, input_val in zip(array.origin_inputs, input_values):
                        input_symb = self.vars[str(input_var)][coord.project(input_var.axes).int_value()]
                        precondition.extend(equals_value(self.symbols[input_symb], input_val))
                    self.clauses.extend(if_then(precondition, statement))
        for var in array.variables:
            self.mark_rendered(var)

    def render_choice_output(self, array: Array, **kwargs):
        self._check_output_correctness(array, ChoiceMapping, 'choice output')
        self._init_array(array)
        choice_id = str(array.origin)
        for inputs, choice_symb in zip(combinations(array.origin_inputs, len(array.variables)), self.choices[choice_id]):
            for inp, var in zip(inputs, array.variables):
                equal_cond = self.equal_vars(inp, var)
                self.clauses.extend(
                    if_then(
                        [self.symbols[choice_symb]],
                        equal_cond,
                    )
                )
        for var in array.variables:
            self.mark_rendered(var)

    def render_function_mapping(self, function: FunctionMapping, **kwargs):
        fun_id = str(function)
        for out_ind in range(function.output_degree):
            for input_id, input in enumerate(all_inputs(function.input_degree)):
                symbol = f'{fun_id}_{out_ind}_{input_id}'
                self.functions[fun_id][out_ind].append(symbol)
                symbol_id = self.symbols[symbol]
                if input in function.values[out_ind]:
                    self.clauses.append(equals_value(symbol_id, function.values[out_ind][input]))
        self.mark_rendered(function)

    def render_choice_mapping(self, choice: ChoiceMapping, **kwargs):
        choice_id = str(choice)
        for indices in combinations(range(choice.input_degree), choice.output_degree):
            self.choices[choice_id].append(f'{choice_id}_{"_".join(map(str, indices))}')
        self.clauses.extend(
            exactly_one([self.symbols[symbol] for symbol in self.choices[choice_id]])
        )
        self.mark_rendered(choice)

    def set_equal(self, *variables, **kwargs):
        self.clauses.extend(self.equal_vars(*variables))

    def equal_vars(self, *variables):
        result = []
        for var in variables:
            assert str(var) in self.vars, f'Variable {var} is not initialized'
        axes = closure(*[var.axes for var in variables])
        for coord in axes:
            symbs = [self.vars[str(var)][coord.project(var.axes).int_value()] for var in variables]
            for symb1, symb2 in encouple(symbs):
                result.extend(equal_symbols(self.symbols[symb1], self.symbols[symb2]))
        return result

    def _check_output_correctness(self, array, correct_mapping_cls, output_name='mapping output'):
        assert isinstance(array.origin, correct_mapping_cls), \
            f'Trying to render {output_name} while origin is not a {correct_mapping_cls.__name__}, but a {type(array.origin)}'
        for var1, var2 in encouple(array.variables):
            assert var1.axes == var2.axes, 'Output variables must have the same axes'

    def _init_array(self, array):
        for var in array.variables:
            if str(var) not in self.vars:
                self.init_variable(var)
