from utils import encouple
from universal.basic import ChoiceMapping, FunctionMapping
from universal.extended import Gate, Circuit


class MappingResult:
    def __init__(self, input_degree, output_degree):
        self.input_degree = input_degree
        self.output_degree = output_degree

    def is_valid(self) -> bool:
        raise NotImplementedError


class ChoiceMappingResult(MappingResult):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        assert all([0 <= choice < self.input_degree for choice in choices]), \
            f'Choice of of bounds [0, {self.input_degree}): {choices}'
        assert len(choices) == self.output_degree, f'Must have {self.output_degree} choices, but have {len(choices)}'
        assert all((left < right for left, right in encouple(choices))), f'Choices are not sorted: {choices}'
        self.choices = choices

    def is_valid(self) -> bool:
        return True


class FunctionMappingResult(MappingResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.values = [{} for _ in range(self.output_degree)]
        self.input_space_size = 2 ** self.input_degree

    def set_value(self, input_index, output_value, output_index):
        assert input_index not in self.values[output_index], f'Index {input_index} is already set for output {output_index}'
        assert 0 <= input_index < self.input_space_size, f'Input index must be in range [0, {self.input_space_size})'
        self.values[output_index][input_index] = output_value

    def is_valid(self) -> bool:
        return all((len(out) == self.input_space_size for out in self.values))


class GateResult(MappingResult):
    def __init__(self, choice_result: ChoiceMappingResult, function_result: FunctionMappingResult):
        super().__init__(input_degree=choice_result.input_degree, output_degree=1)
        assert function_result.output_degree == 1, 'Gate output must be of degree 1'
        self.choice_result = choice_result
        self.function_result = function_result

    def is_valid(self) -> bool:
        return self.choice_result.is_valid() and self.function_result.is_valid()


class CircuitResult(MappingResult):
    def __init__(self, gate_results: list, choice_result: ChoiceMappingResult):
        super().__init__(input_degree=choice_result.input_degree - len(gate_results), output_degree=choice_result.output_degree)
        self.gate_results = gate_results
        self.choice_result = choice_result

    def is_valid(self) -> bool:
        return all([gate_result.is_valid() for gate_result in self.gate_results]) and self.choice_result.is_valid()


class Decoder:
    def consume_model(self, model):
        raise NotImplementedError

    def get_choice_result(self, choice: ChoiceMapping) -> ChoiceMappingResult:
        raise NotImplementedError

    def get_function_result(self, func: FunctionMapping) -> FunctionMappingResult:
        raise NotImplementedError

    def get_gate_result(self, gate: Gate) -> GateResult:
        choice_result = self.get_choice_result(gate.choice)
        function_result = self.get_function_result(gate.function)
        return GateResult(choice_result=choice_result, function_result=function_result)

    def get_circuit_result(self, circuit: Circuit) -> CircuitResult:
        gate_results = [self.get_gate_result(gate) for gate in circuit.gates]
        choice_result = self.get_choice_result(circuit.choice)
        return CircuitResult(gate_results=gate_results, choice_result=choice_result)
