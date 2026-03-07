import asyncio
import random

class RedQueenPredator:
    def __init__(self, instance_manager):
        self.im = instance_manager
        self.distance = 100 # Starting distance
        self.base_speed = 5 # Closes 5 distance units per tick
        self.hunting = False
        
    async def run_hunt_loop(self):
        self.hunting = True
        print("Predator Engine Initialized. Red Queen Dynamics Active.")
        
        while self.hunting:
            await asyncio.sleep(1.0) # Tick rate
            
            agent = self.im.active_agent
            if not agent or agent.state in ["INCUBATING", "DYING"]:
                self.distance = 100 # Reset distance when agent dies/respawns
                continue
                
            # Predator evolves slightly faster as generations increase
            current_speed = self.base_speed + (self.im.generation * 0.5)
            
            # Prey (Agent) evades slightly when in the ACTING state (processing prompts well)
            if agent.state == "ACTING":
                 evasion = random.uniform(2, 8)
                 self.distance += evasion
                 
            # Predator moves closer
            self.distance -= current_speed
            self.distance = max(0, min(100, self.distance))
            
            # Update agent telemetry with predator distance
            agent.predator_distance = f"{self.distance:.1f}m"
            
            # Attack! If distance is 0, predator drains massive energy
            if self.distance <= 0:
                print(f"[PREDATOR STRIKE] Agent {agent.id} taking 20 damage!")
                agent.energy -= 20.0
                self.distance = 50 # Predator backs off after strike

            # Force UI update
            asyncio.create_task(self.im.broadcast(agent.get_telemetry()))
