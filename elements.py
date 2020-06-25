class Element:
    def __init__(self, backend):
        self.backend = backend


class Variable(Element):
    typename = 'var'

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self._full_name = f'{self.typename}_{self.name}'

    @property
    def full_name(self):
        return self._full_name


class InputVariable(Variable):
    typename = 'input'


class Block(Element):
    input_size = None
    output_size = None


class Choice(Block):
    pass


class Function(Block):
    output_size = 1


class SmallFunction(Function):
    input_size = 2
