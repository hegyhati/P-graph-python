from dataclasses import dataclass
import json
from typing import FrozenSet


@dataclass(frozen=True)
class Material():
    display_name: str
    id: str


@dataclass(frozen=True)
class Operating_unit():
    display_name: str
    inputs: FrozenSet[Material]
    outputs: FrozenSet[Material]


class P_graph:
    def __init__(self, filename: str = None, data: dict = None) -> None:
        if filename:
            with open(filename) as file:
                data = json.load(file)

        if data:
            self._init_from_data_(data)
        else:
            raise ValueError("No data or filename provided")

    def _init_from_data_(self, data: dict) -> None:
        self.materials = {id: Material(
            id=id,
            display_name=m["display_name"]
        ) for id, m in data["materials"].items()}
        self.operating_units = [Operating_unit(
            inputs={self.materials[m] for m in o["inputs"]},
            outputs={self.materials[m] for m in o["outputs"]},
            display_name=o["display_name"]
        ) for o in data["operating_units"]] # should be set

    def __str__(self) -> str:
        return f"""
            M = {{ {", ".join(m.display_name for m in self.materials.values())} }}
            O = {{ {", ".join(o.display_name for o in self.operating_units)} }}
        """
    
    def get_producers(self, material: Material):
        return {o for o in self.operating_units if material in o.outputs}
    
    def get_consumers(self, material: Material):
        return {o for o in self.operating_units if material in o.inputs}

class PNS:
    def __init__(self, filename: str = None, data: dict = None) -> None:
        if filename:
            with open(filename) as file:
                data = json.load(file)

        if data:
            self.p_graph = P_graph(data=data)
            self.products = {self.p_graph.materials[id] for id in data["problem"]["products"]}
            self.raw_materials = {self.p_graph.materials[id] for id in data["problem"]["raw_materials"]}
        else:
            raise ValueError("No data or filename provided")
    
    def __str__(self) -> str:
        return f"""
            P-graph:  {self.p_graph}
            Products: {", ".join([m.display_name for m in self.products])}
            Raw materials: {", ".join([m.display_name for m in self.raw_materials])}
        """

    

    


if __name__ == "__main__":
    print(PNS("examples/ThePgraph.json"))
