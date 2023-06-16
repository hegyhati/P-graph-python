import json
import os
from sys import argv
import pandas as pd

pnsfile = argv[1]
modeldir = argv[2]

def fetch_gmpl_snippets(file):
    print(file)
    with open(file) as f:
        data = json.load(f)
    return [
        {"name": o["display_name"], "gmpl": o["gmpl"]}
        for o in data["operating_units"]
        if "gmpl" in o
    ]

constraints = fetch_gmpl_snippets(pnsfile)

rows = {}
counter = 0
for model in os.listdir(modeldir):
    with open(os.path.join(modeldir,model)) as f:
        modeltext = f.read()
    print(model, counter)
    counter +=1
    rows[model] =  {
        o["name"] : 1 if o["gmpl"] in modeltext else 0
        for o in constraints
    }

df = pd.DataFrame(columns=[o["name"] for o in constraints])
for model in rows:
    df.loc[model] = rows[model]
print(df)

df.to_excel("models.xlsx")
