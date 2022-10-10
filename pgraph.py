from dataclasses import dataclass
import json
from typing import FrozenSet, Set


@dataclass(frozen=True)
class Material():
    display_name: str
    id: str


@dataclass(frozen=True)
class Operating_unit():
    display_name: str
    inputs: FrozenSet[Material]
    outputs: FrozenSet[Material]

    def get_materials(self) -> Set[Material]:
        return self.inputs.union(self.outputs)
    
    def __hash__(self) -> int:
        return id(self)


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
        self.operating_units = {Operating_unit(
            inputs={self.materials[m] for m in o["inputs"]},
            outputs={self.materials[m] for m in o["outputs"]},
            display_name=o["display_name"]
        ) for o in data["operating_units"]}

    def __str__(self) -> str:
        return f"""
            M = {{ {", ".join([m.display_name for m in self.materials.values()])} }}
            O = {{ {", ".join([o.display_name for o in self.operating_units])} }}
        """
    
    def get_producers(self, materials: Set[Material]) -> Set[Operating_unit]:
        return {o for o in self.operating_units for material in materials if material in o.outputs}
    
    def get_consumers(self, materials: Set[Material]) -> Set[Operating_unit]:
        return {o for material in materials for o in self.operating_units if material in o.inputs}
    
    def get_materials(self, operating_units: Set[Operating_unit]) -> Set[Material]:
        return {m for operating_unit in operating_units for m in operating_unit.get_materials()}

    def get_inputs(self, operating_units: Set[Operating_unit]) -> Set[Material]:
        return {m for operating_unit in operating_units for m in operating_unit.inputs}

    def get_outputs(self, operating_units: Set[Operating_unit]) -> Set[Material]:
        return {m for operating_unit in operating_units for m in operating_unit.outputs}

class PNS(P_graph):
    def __init__(self, filename: str = None, data: dict = None) -> None:
        if filename:
            with open(filename) as file:
                data = json.load(file)

        if data:
            super().__init__(data=data)
            self.products = {self.materials[id] for id in data["problem"]["products"]}
            self.raw_materials = {self.materials[id] for id in data["problem"]["raw_materials"]}
        else:
            raise ValueError("No data or filename provided")
    
    def __str__(self) -> str:
        return f"""
            P-graph:  {super().__str__()}
            Products: {", ".join([m.display_name for m in self.products])}
            Raw materials: {", ".join([m.display_name for m in self.raw_materials])}
        """
    
    def reduce_by_MSG(self):
        possible_units = self.operating_units - self.get_producers(self.raw_materials)
        possible_materials = self.get_materials(possible_units)
        not_produced_materials = self.get_inputs(possible_units) - self.get_outputs(possible_units) - self.raw_materials

        while not_produced_materials:
            m = not_produced_materials.pop()
            possible_materials.remove(m)
            m_consumers = self.get_consumers({m})
            possible_units -= m_consumers
            not_produced_materials.update(self.get_outputs(m_consumers) - self.get_outputs(possible_units) - self.raw_materials)
        
        if not self.products.issubset(possible_materials):
            raise ValueError("There is no solution structure")
        
        to_be_produced = self.products.copy()
        final_materials = set()
        final_units = set()

        while to_be_produced:
            m = to_be_produced.pop()
            final_materials.add(m)
            m_producers = self.get_producers({m})
            final_units.update(m_producers)
            to_be_produced.update(self.get_inputs(m_producers) - final_materials - self.raw_materials)
        
        self.materials = {m.id : m for m in self.get_materials(final_units)}
        # self.raw_materials.intersection_update(self.materials) # necessity will be decided later
        self.operating_units = final_units 


if __name__ == "__main__":
    pns = PNS("examples/ThePgraph.json")
    print(pns)
    pns.reduce_by_MSG()
    print(pns)