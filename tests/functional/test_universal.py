import pytest

from engines import AVAILABLE_ENGINES
from universal import Variable, ChoiceMapping, FunctionMapping


@pytest.mark.parametrize('engine_cls', AVAILABLE_ENGINES)
def test_simple_choice(engine_cls):
    engine = engine_cls()
    variables = [Variable(), Variable(), Variable()]
    choice = ChoiceMapping(output_degree=2, input_degree=3)
    result = choice(variables)
    result.render(engine)


@pytest.mark.parametrize('engine_cls', AVAILABLE_ENGINES)
def test_simple_function(engine_cls):
    engine = engine_cls()
    variables = [Variable(), Variable(), Variable()]
    fun = FunctionMapping(output_degree=2, input_degree=3)
    result = fun(variables)
    result.render(engine)
