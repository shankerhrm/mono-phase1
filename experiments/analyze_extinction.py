import json

with open("phase8_ecology_results.json") as f:
    history = json.load(f)

# The simulation stops at extinction. I need to get the actual history from the cells!
# Let me re-run and save the final cells' history.
