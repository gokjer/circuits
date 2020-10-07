from math import log2, ceil

from utils import all_inputs
from universal import FunctionMapping


def minimal_dim(max_value):
    return ceil(log2(max_value + 1))


class FunctionTemplate:
    def __init__(self, input_degree, output_degree, computer):
        self.input_degree = input_degree
        self.output_degree = output_degree
        self.computer = computer

    def set_truthtable(self, function: FunctionMapping, zerofill=True):
        for inp in all_inputs(dim=self.input_degree):
            output = self.computer(inp)
            if len(output) < self.output_degree:
                assert zerofill, f'Output "{output}" is too short, but filling with zeroes is prohibited'
                output = [0] * (self.output_degree - len(output)) + output
            for index, value in enumerate(output):
                function.set_value(input_values=inp, output_index=index, output_value=value)

    def make_function(self) -> FunctionMapping:
        function = FunctionMapping(input_degree=self.input_degree, output_degree=self.output_degree)
        self.set_truthtable(function)
        return function


def number_to_list(n: int, pad=0):
    return list(map(int, f'{n:b}'.zfill(pad)))


def list_to_number(l: list):
    return int(''.join(map(lambda x: str(int(x)), l)), 2)


def mod_value_computer(n, dim=None):
    dim = dim or minimal_dim(n-1)

    def computer(inputs):
        int_value = sum(inputs)
        result_value = int_value % n
        return number_to_list(result_value, pad=dim)

    return computer


def mod_n_k_computer(n, k):
    assert 0 <= k < n, 'k must be in [0, n)'

    def computer(inputs):
        int_value = sum(inputs)
        result_value = int((int_value % n) == k)
        return number_to_list(result_value)

    return computer


def mod_n_comb_computer(n, dim=None):
    dim = dim or minimal_dim(n-1)

    def computer(inputs):
        buffer = inputs[-dim:]
        inputs = inputs[:-dim]
        result = (list_to_number(buffer) + sum(inputs)) % n
        return number_to_list(result, pad=dim)

    return computer
