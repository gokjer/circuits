from itertools import combinations

from universal.result import Decoder, FunctionMappingResult, ChoiceMappingResult


class SATDecoder(Decoder):
    """
    Must also inherit SATEngine
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol_values = None

    def get_choice_result(self, choice) -> ChoiceMappingResult:
        self._check_model_consumed()
        choice_id = str(choice)
        for symbol, indices in zip(self.choices[choice_id], combinations(range(choice.input_degree), choice.output_degree)):
            if self.symbol_values[self.symbols[symbol]]:
                return ChoiceMappingResult(indices, input_degree=choice.input_degree, output_degree=choice.output_degree)
        assert False, 'No choice was marked as a correct one'

    def get_function_result(self, func) -> FunctionMappingResult:
        self._check_model_consumed()
        result = FunctionMappingResult(input_degree=func.input_degree, output_degree=func.output_degree)
        func_id = str(func)
        for out_ind in range(func.output_degree):
            for index, symb in enumerate(self.functions[func_id][out_ind]):
                output_value = self.symbol_values[self.symbols[symb]]
                result.set_value(input_index=index, output_index=out_ind, output_value=output_value)
        assert result.is_valid(), f'Could not fill result for FunctionMapping {func}'
        return result

    def consume_model(self, model):
        self.symbol_values = []
        for val in model:
            assert abs(val) == len(self.symbol_values) + 1
            self.symbol_values.append(val > 0)

    def _check_model_consumed(self):
        assert self.symbol_values is not None, 'Must consume model before getting results'
