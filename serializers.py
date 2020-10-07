from collections import defaultdict

from universal import GateResult, CircuitResult


truthtable_decoder = defaultdict(lambda: ('', '*', ''))
truthtable_decoder['0001'] = ('', '&', '')
truthtable_decoder['0010'] = ('', '&', '-')
truthtable_decoder['0100'] = ('-', '&', '')
truthtable_decoder['1000'] = ('-', '&', '-')
truthtable_decoder['0111'] = ('', '|', '')
truthtable_decoder['1011'] = ('', '|', '-')
truthtable_decoder['1101'] = ('-', '|', '')
truthtable_decoder['1110'] = ('-', '|', '-')
truthtable_decoder['0110'] = ('', '^', '')
truthtable_decoder['1001'] = ('', '==', '')


def get_truthtable(fun_result):
    assert fun_result.input_degree == 2 and fun_result.output_degree == 1, 'Function must be 2 -> 1'
    return ''.join(map(str, map(int, map(lambda p: p[1], sorted(fun_result.values[0].items())))))


def serialize_gate(gate_result: GateResult):
    vars = gate_result.choice_result.choices
    left_name, right_name = [f'x{var}' for var in vars]
    name = f'x{gate_result.input_degree}'
    truthtable = get_truthtable(gate_result.function_result)
    lsign, op, rsign = truthtable_decoder[truthtable]
    appendix = ''
    if op == '*':
        appendix = f' ({truthtable})'
    return f'{name} = {lsign}{left_name} {op} {rsign}{right_name}{appendix}'


def serialize_circuit(circuit_result: CircuitResult, sep='\n'):
    result = [
        '===========Circuit results===========',
        f'x0..x{circuit_result.input_degree-1} -- inputs, x{circuit_result.input_degree}..x{circuit_result.input_degree + len(circuit_result.gate_results) - 1} -- gates',
    ]
    for gate_result in circuit_result.gate_results:
        result.append(serialize_gate(gate_result))
    result.append(
        ', '.join(
            [f'x{choice}' for choice in circuit_result.choice_result.choices]
        )
    )
    result.append('=====================================')
    return sep.join(result)
