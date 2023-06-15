from itertools import combinations
import json
from typing import Set
from pgraph import PNS, Operating_unit, Material
import os
import os.path


class Generator(PNS):
    def __init__(self, filename: str = None, directory: str = "models", limit : int = 10) -> None:
        super().__init__(filename)
        self.directory = os.path.join(os.curdir, directory)
        self.limit = limit
        with open(filename) as f:
            self.data = json.load(f)
        os.mkdir(self.directory)


    def generate_models(self) -> None:
        self.counter=0
        return self._generator_subroutine(set(), set(), set(), self.products)
    
    def _persist_model(self, included) -> None:
        materials = self.get_materials(included)
        material_ids = [m.id for m in materials]
        for m in materials:
            for incompatible in m.incompatible:
                if incompatible in material_ids:
                    return
        if self.counter < self.limit :
            with open(os.path.join(self.directory, f"{self.counter}.mod"), "w") as f:
                for line in self.data["global_statements"]["pre"]:
                    f.write(line + "\n")
                f.write("\n")
                for m in self.get_materials(included):
                    if "gmpl" in self.data["materials"][m.id]:
                        f.write(self.data["materials"][m.id]["gmpl"] + "\n")
                f.write("\n")
                for o in included:
                    if "gmpl" in self.data["operating_units"][o.idx]:
                        f.write(self.data["operating_units"][o.idx]["gmpl"] + "\n")
                f.write("\n")
                for line in self.data["global_statements"]["post"]:
                    f.write(line + "\n")
        self.counter += 1


    
    def _generator_subroutine(self, included: Set[Operating_unit], excluded: Set[Operating_unit], decided_materials: Set[Material], undecided_materials: Set[Material]) -> None:
        if self.counter >= self.limit : return
        undecided_materials = undecided_materials.copy()
        if not undecided_materials:
            self._persist_model(included)
            return

        m = undecided_materials.pop()
        for incompatible in m.incompatible:
            if incompatible in decided_materials:
                return

        m_producers = self.get_producers({m})
        if not m_producers - excluded:
            return 
        
        undecided_m_producers = m_producers - excluded - included
        if not undecided_m_producers:
            return self._generator_subroutine(included, excluded, decided_materials.union({m}), undecided_materials)
        
        for size in range(0 if m_producers.intersection(included) else 1, len(undecided_m_producers)+1):
            for include in combinations(undecided_m_producers,size):
                self._generator_subroutine(
                    included.union(include), 
                    excluded.union(undecided_m_producers.difference(include)),
                    decided_materials.union({m}),
                    undecided_materials.union(self.get_inputs(include) - decided_materials - {m} - self.raw_materials)
                )

    def run_tests(self, example:str):
        for model in range(self.limit):
            print(f"glpsol -m {os.path.join(self.directory, f'{model}.mod')} -d {example} -y {os.path.join(self.directory, f'{model}.out')}")
            os.system(f"glpsol -m {os.path.join(self.directory, f'{model}.mod')} -d {example} -y {os.path.join(self.directory, f'{model}.out')}")




from sys import argv
if __name__ == "__main__":
    generator = Generator(argv[1], directory=argv[2], limit=int(argv[3]))
    print(generator)
    generator.reduce_by_MSG()
    print(generator, len(generator.operating_units))
    generator.generate_models()
    print(generator, len(generator.operating_units))
    # generator.run_tests('examples/precedence.dat')