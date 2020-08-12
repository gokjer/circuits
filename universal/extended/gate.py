from universal.basic import RenderableMapping, ChoiceMapping, FunctionMapping


class Gate(RenderableMapping):
    def __init__(self, input_degree):
        super().__init__(input_degree, output_degree=1)
        self.choice = ChoiceMapping(input_degree=self.input_degree, output_degree=2)
        self.function = FunctionMapping(input_degree=2, output_degree=1)

    def __call__(self, input_vars, **kwargs):
        choices_array = self.choice(input_vars, **kwargs)
        return self.function(choices_array.variables, **kwargs)

    def do_render(self, renderer, **kwargs):
        self.choice.render(renderer, **kwargs)
        self.function.render(renderer, **kwargs)
