import subprocess
import os
import enum
try:
    from pysat.solvers import *
except ImportError:
    pass


class SolveStatuses(enum.Enum):
    NOT_RAN = enum.auto()
    SAT = enum.auto()
    UNSAT = enum.auto()


class BinarySolver:
    def __init__(self, path):
        self.path = path
        self.clauses = []
        self.options = []
        self.status = SolveStatuses.NOT_RAN
        self.model = None

    def add_clause(self, clause):
        self.clauses.append(clause)

    def add_option(self, option):
        self.options.append(option)

    def get_model(self):
        return self.model

    def solve(self):
        self.prepare()
        input_path = self._get_tmp_path()
        self._write_clauses(input_path)
        out_path = 'out.sat'
        cmd = [self.path]
        for option in self.options:
            cmd.append(option)
        cmd.extend([input_path, out_path])
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in iter(proc.stdout.readline, b''):
            # print(line.decode(), end='')
            if line.startswith(b's'):
                if line.find(b'UNSAT') >= 0:
                    self.status = SolveStatuses.UNSAT
                else:
                    self.status = SolveStatuses.SAT
            if line.startswith(b'v'):
                self.model = list(map(int, line.rstrip()[2:-2].split()))
        os.remove(input_path)
        return self.status is SolveStatuses.SAT

    def _write_clauses(self, tmp_path='tmp.sat'):
        n = self._compute_variables()
        m = len(self.clauses)
        with open(tmp_path, 'w') as file:
            file.write(f'p cnf {n} {m}\n')
            for clause in self.clauses:
                file.write(f'{" ".join(map(str, clause))} 0\n')

    def _compute_variables(self):
        vars = set()
        for clause in self.clauses:
            vars.update((-v if v < 0 else v for v in clause))
        return len(vars)

    def _get_tmp_path(self):
        return 'tmp.sat'

    def prepare(self):
        pass


class Syrup(BinarySolver):
    name = 'glucose-syrup'
    max_threads = 32

    def __init__(self, path='./glucose-syrup_static', max_threads=None):
        super().__init__(path)
        if max_threads is not None:
            self.max_threads = max_threads

    def prepare(self):
        self.add_option(f'-maxnbthreads={self.max_threads}')
        self.add_option('-model')
