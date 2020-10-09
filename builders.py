from universal import Variable, Circuit, FunctionMapping, make_equalities
from computers import FunctionTemplate
from utils import time_and_log


class BaseBuilder:
    def __init__(self, engine, solver):
        self.engine = engine
        self.solver = solver
        self.success = None
        self.equalities = []

    def initialize(self, **kwargs):
        raise NotImplementedError

    def build(self, **kwargs):
        raise NotImplementedError

    def render(self, **kwargs):
        for eq in self.equalities:
            eq.render(self.engine, **kwargs)

    def solve(self, **kwargs):
        self.engine.init_solver(self.solver)
        self.engine.log_stat()
        return self.solver.solve()

    def decode(self, **kwargs):
        self.engine.consume_model(self.solver.get_model())

    def prepare(self, **kwargs):
        print(f'{self.__class__.__name__} preparation')
        self.log_parameters()
        with time_and_log('Initialization'):
            self.initialize(**kwargs)
        with time_and_log('Building'):
            self.build(**kwargs)
        with time_and_log('Rendering'):
            self.render(**kwargs)

    def run(self, **kwargs):
        with time_and_log('Solving'):
            self.success = self.solve(**kwargs)
        print(f'Success: {self.success}')
        if self.success:
            self.decode(**kwargs)

    def log_parameters(self):
        raise NotImplementedError


class SimpleBuilder(BaseBuilder):
    def __init__(self, input_degree, output_degree, n_gates, true_fun_computer, **kwargs):
        super().__init__(**kwargs)
        self.input_degree = input_degree
        self.output_degree = output_degree
        self.n_gates = n_gates
        self.true_fun_computer = true_fun_computer

    def initialize(self, **kwargs):
        self.inputs = [Variable() for _ in range(self.input_degree)]
        self.circuit = Circuit(input_degree=self.input_degree, output_degree=self.output_degree, n_gates=self.n_gates)
        self.true_fun = FunctionTemplate(input_degree=self.input_degree, output_degree=self.output_degree, computer=self.true_fun_computer).make_function()

    def build(self, **kwargs):
        self.circuit_output = self.circuit(self.inputs)
        self.true_output = self.true_fun(self.inputs)
        self.equalities.extend(make_equalities(self.circuit_output, self.true_output))

    def decode(self, **kwargs):
        super().decode(**kwargs)
        self.circuit_result = self.engine.get_circuit_result(self.circuit)

    def log_parameters(self):
        print(f'input_degree={self.input_degree}, output_degree={self.output_degree}, n_gates={self.n_gates}')


class RecurseBuilder(BaseBuilder):
    def __init__(self, input_degree, output_degree, n_gates, buffer_size, true_comb_computer, **kwargs):
        super().__init__(**kwargs)
        self.input_degree = input_degree
        self.output_degree = output_degree
        self.n_gates = n_gates
        self.buffer_size = buffer_size
        self.true_comb_computer = true_comb_computer

    def log_parameters(self):
        print(f'input_degree={self.input_degree}, output_degree={self.output_degree}, n_gates={self.n_gates}, buffer_size={self.buffer_size}')

    def initialize(self, **kwargs):
        self.inputs = [Variable() for _ in range(self.input_degree)]
        self.buffer_inputs = [Variable() for _ in range(self.buffer_size)]
        self.circuit = Circuit(input_degree=self.input_degree + self.buffer_size, output_degree=self.buffer_size, n_gates=self.n_gates)
        self.inv = FunctionMapping(input_degree=self.buffer_size, output_degree=self.output_degree)
        self.true_fun = FunctionTemplate(input_degree=self.input_degree+self.output_degree, output_degree=self.output_degree, computer=self.true_comb_computer).make_function()

    def build(self, **kwargs):
        self.circuit_output = self.circuit(self.inputs + self.buffer_inputs)
        self.inv_output = self.inv(list(self.circuit_output))
        self.true_output = self.true_fun(self.inputs + list(self.inv(self.buffer_inputs)))
        self.equalities.extend(make_equalities(self.inv_output, self.true_output))

    def decode(self, **kwargs):
        super().decode(**kwargs)
        self.circuit_result = self.engine.get_circuit_result(self.circuit)
        self.inv_result = self.engine.get_function_result(self.inv)
