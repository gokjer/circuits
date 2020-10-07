from universal.basic import RenderableMapping, ChoiceMapping
from universal.extended import Gate


class Circuit(RenderableMapping):
    def __init__(self, input_degree, output_degree, n_gates):
        super().__init__(input_degree, output_degree)
        self.gates = [Gate(input_degree=self.input_degree + i) for i in range(n_gates)]
        self.choice = ChoiceMapping(input_degree=self.input_degree + n_gates, output_degree=self.output_degree)

    def __call__(self, input_vars, **kwargs):
        variables = list(input_vars)
        for gate in self.gates:
            variables.extend(gate(variables, **kwargs))
        return self.choice(variables, **kwargs)

    def do_render(self, renderer, **kwargs):
        for gate in self.gates:
            gate.render(renderer, **kwargs)
        self.choice.render(renderer, **kwargs)
