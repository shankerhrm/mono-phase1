import asyncio
import uuid
import time
import random
from phase29_species_memory import SpeciesMemoryDB

class MonoAgent:
    def __init__(self, generation, traits, starting_energy=100):
        self.id = f"AG-{str(uuid.uuid4())[:8].upper()}"
        self.generation = generation
        self.age = 0
        self.energy = starting_energy
        self.state = "INCUBATING" # INCUBATING, BREATHING, HEARING, ACTING, DYING
        self.fitness = 0
        self.predator_distance = "N/A"
        self.traits = traits
        
    def get_telemetry(self):
        return {
            "instance_id": self.id,
            "generation": self.generation,
            "age": self.age,
            "energy": round(self.energy, 1),
            "state": self.state,
            "predator_distance": self.predator_distance,
            "traits": self.traits
        }

class InstanceManager:
    def __init__(self, broadcast_callback):
        self.db = SpeciesMemoryDB()
        self.generation = self.db.get_latest_generation() + 1
        self.active_agent = None
        self.broadcast = broadcast_callback
        self.running = False
        
    async def run_ecosystem(self):
        self.running = True
        while self.running:
            # 1. Birth
            if self.active_agent is None or self.active_agent.energy <= 0:
                await self.spawn_agent()
                
            # 2. Breathing (Basal Metabolism)
            if self.active_agent.state == "BREATHING":
                self.active_agent.energy -= 0.5 # Burn 0.5 energy per cycle
                self.active_agent.age += 1
                
            # 3. Death Check
            if self.active_agent.energy <= 0:
                print(f"Agent {self.active_agent.id} starved.")
                self.active_agent.state = "DYING"
                await self.broadcast(self.active_agent.get_telemetry())
                await asyncio.sleep(1) # Dramatic pause for death
                self.commit_to_species_memory()
                self.active_agent = None
                self.generation += 1
                continue
                
            # Broadcast state
            await self.broadcast(self.active_agent.get_telemetry())
            await asyncio.sleep(1.0) # 1 tick per second
            
    async def spawn_agent(self):
        print(f"Spawning Generation {self.generation}...")
        
        # Pull best traits and apply Mutation (Drift)
        parent_traits = self.db.get_best_traits()
        child_traits = {
            "temperature": max(0.1, min(2.0, parent_traits["temperature"] + random.uniform(-0.1, 0.1))),
            "top_p": max(0.1, min(1.0, parent_traits["top_p"] + random.uniform(-0.05, 0.05))),
            "heuristic_genes": parent_traits["heuristic_genes"] # For now, exact copy of heuristics
        }
        
        self.active_agent = MonoAgent(self.generation, child_traits)
        await self.broadcast(self.active_agent.get_telemetry())
        await asyncio.sleep(2) # Incubation latency
        self.active_agent.state = "BREATHING"
        
    async def process_query(self, query):
        if not self.active_agent or self.active_agent.state == "DYING":
            return "(Agent is currently deceased or incubating)"
            
        print(f"{self.active_agent.id} Heard: {query}")
        
        # 1. Hearing
        self.active_agent.state = "HEARING"
        await self.broadcast(self.active_agent.get_telemetry())
        await asyncio.sleep(1) # Simulation of processing delay
        self.active_agent.energy -= 2.0 # Hearing costs energy
        
        # 2. Acting (Replace with LLM later)
        self.active_agent.state = "ACTING"
        await self.broadcast(self.active_agent.get_telemetry())
        
        # Simulated LLM processing based on inherited temperature
        temp = self.active_agent.traits['temperature']
        await asyncio.sleep(1.0 + random.uniform(0.1, 1.0) * temp)
        
        # Generating a simulated response using the agent's heuristic genes
        gene_influence = " | ".join(self.active_agent.traits['heuristic_genes'])
        response = f"[Gen {self.generation} | Temp: {temp:.2f}]\n\nProcessing: '{query}'\nApplying Heuristics: [{gene_influence}]\n\nSimulation OK. Energy -5 for action, +15 for successful task completion."
        
        self.active_agent.energy -= 5.0 # Action cost
        
        # Reward
        self.active_agent.energy += 15.0 # Success reward
        self.active_agent.fitness += 1
        
        # Return to breathing
        self.active_agent.state = "BREATHING"
        await self.broadcast(self.active_agent.get_telemetry())
        
        return response

    def commit_to_species_memory(self):
        self.db.record_generation(
            generation=self.generation,
            fitness=self.active_agent.fitness,
            temperature=self.active_agent.traits["temperature"],
            top_p=self.active_agent.traits["top_p"],
            heuristic_genes=self.active_agent.traits["heuristic_genes"]
        )
        print(f"Memory stored for Gen {self.generation}. Fitness: {self.active_agent.fitness}")
