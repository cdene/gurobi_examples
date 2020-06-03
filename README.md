# gurobi_examples
Practicing mathematical optimisation. 
Examples from https://www.gurobi.com/resource/hp-williams-modeling-examples/
https://www.gurobi.com/documentation/9.0/examples

Setting up environment:
```bash
conda env create -f gurobi-examples-env.yml
conda activate gurobi-examples-env
```

Updating environment:
```bash
conda env update --file gurobi-examples-env.yml --prune
```

1) Facility location
```bash
python facility/facility.py
```
