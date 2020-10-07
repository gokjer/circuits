import pytest

from engines import AVAILABLE_ENGINES
from universal import Variable, Gate, Equality
from computers import mod_value_computer, FunctionTemplate
from solvers import AVAILABLE_SOLVERS


@pytest.mark.parametrize('engine_cls, solver_cls', [(engine, solver) for engine in AVAILABLE_ENGINES for solver in AVAILABLE_SOLVERS[engine]])
def test_xor(engine_cls, solver_cls):
    engine = engine_cls()
    variables = [Variable(), Variable()]
    gate = Gate(input_degree=len(variables))
    result = gate(variables)

    true_function = FunctionTemplate(input_degree=len(variables), output_degree=1,
                                     computer=mod_value_computer(2)).make_function()
    true_output = true_function(variables)
    equality = Equality([*result, *true_output])
    equality.render(engine)

    solver = solver_cls()
    for clause in engine.clauses:
        solver.add_clause(clause)
    assert solver.solve()
    model = solver.get_model()
    engine.consume_model(model)
    gate_result = engine.get_gate_result(gate)
    true_fun_result = engine.get_function_result(true_function)
    assert gate_result.function_result.values == true_fun_result.values
