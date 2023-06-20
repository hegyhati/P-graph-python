import json
from sys import argv
import pydot 


style = {"penwidth" : 3}
with open(argv[1]) as f:
    data = json.load(f)

g = pydot.Dot('my_graph', graph_type='digraph', ratio=0.6)

R = pydot.Subgraph(rank='source')
P = pydot.Subgraph(rank='sink')
I = pydot.Subgraph()


for m in data["materials"]:
    if m == "FORBIDDENPRODUCT": continue
    if m in data["problem"]["products"]:
        P.add_node(pydot.Node(m,label='', shape='doublecircle',height=1, **style))
    elif m in data["problem"]["raw_materials"]:
        R.add_node(pydot.Node(m,label='', shape='invtriangle',height=1, width=2, **style))
    else:
        I.add_node(pydot.Node(m,label='', style='filled', shape='circle',height=1 , **style))

g.add_subgraph(R)
g.add_subgraph(I)
g.add_subgraph(P)

for o in data["operating_units"]:
    oid=o["display_name"]
    g.add_node(pydot.Node(oid, label='', shape='rectangle', style='filled', fillcolor='black', width=4, height=0.2))
    for m in o["inputs"]:
        g.add_edge(pydot.Edge(m,oid,arrowsize=3, **style))
    for m in o["outputs"]:
        g.add_edge(pydot.Edge(oid,m,arrowsize=3, **style))



g.write_raw(argv[1]+".dot")
g.write_png(argv[1]+".png")

