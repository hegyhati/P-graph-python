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
        ) for o in data["operating units"]] # should be set

    def __str__(self) -> str:
        return f"""
            M = {{ {", ".join(m.display_name for m in self.materials.values())} }}
            O = {{ {", ".join(o.display_name for o in self.operating_units)} }}
        """


if __name__ == "__main__":
    print(P_graph("examples/ThePgraph.json"))
