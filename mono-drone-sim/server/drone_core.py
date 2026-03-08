import sys
import os
from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List, Optional
import json

# Add parent directory to path to import SpeciesMemory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from species_memory import SpeciesMemory

app = FastAPI(title="MONO Drone Core")

# Initialize Species Memory
memory = SpeciesMemory()

class DroneState(BaseModel):
    id: str
    x: float
    y: float
    vx: float
    vy: float
    landed: bool
    energy: float
    fitness: float
    collision: bool

@app.post("/api/drone/telemetry")
async def report_telemetry(drones: List[DroneState]):
    """
    Receive telemetry from the simulation and update species memory.
    """
    organism_data = []
    for d in drones:
        # Map drone metrics to SpeciesMemory phi format:
        # phi = (tau_i, E_i, gamma_i, A_i, R_i, S_i)
        # S_i is survival (landed = 1, crashed/collision = 0)
        phi = (
            abs(d.vx) + abs(d.vy), # proxy for tau (latency/activity)
            d.energy,              # E_i
            0.5,                   # gamma (placeholder)
            {"id": d.id},          # A_i (architecture metadata)
            0.0,                   # R_i (restoration)
            1 if d.landed else 0   # S_i (survival)
        )
        organism_data.append(phi)
    
    # Update Species Memory based on survivors
    memory.update(organism_data)
    
    print(f"Telemetry received for {len(drones)} drones. Ms: {memory.Ms}")
    return {"status": "ok", "ms": memory.Ms}

@app.post("/api/drone/control")
async def get_control(drone: DroneState):
    """
    Returns the next command for a drone based on its state and current species memory.
    """
    # Currently using a heuristic derived from target center (400, 525)
    # In future phases, this will use evolved weights from memory.Ms
    target_x = 400
    target_y = 525
    
    dx = target_x - drone.x
    dy = target_y - drone.y
    
    if abs(dx) < 5 and abs(dy) < 5:
        return {"command": None}
        
    # Evolve threshold sensitivity based on energy ceiling (example of Ms influence)
    # If energy_ceiling is low, become more "cautious" or "direct"
    
    if abs(dx) > abs(dy):
        command = "right" if dx > 0 else "left"
    else:
        command = "down" if dy > 0 else "up"
        
    return {"command": command}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
