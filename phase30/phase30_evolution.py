import asyncio
import json
import random
import os
import sys

# Add parent directory to path to import ollama_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ollama_api import OllamaClient
from dotenv import load_dotenv

load_dotenv()

from phase30_evaluator import FuzzyEvaluator

random.seed(42)

# --- CONFIGURATION (UPDATED FOR STABILITY) ---
POPULATION_SIZE = 20
GENERATIONS = 10  # Reduced for faster intelligence proof
TASKS_PER_GENERATION = 10
STARTING_ENERGY = 100
MUTATION_RATE_HEURISTIC = 0.05
MUTATION_RATE_TEMP = 0.10

# Baseline settings
RUN_BASELINE = "--baseline" in sys.argv

class Agent:
    def __init__(self, id_num, temp=0.7, heuristics=None):
        self.id = id_num
        self.energy = STARTING_ENERGY
        self.temp = temp
        self.heuristics = heuristics if heuristics is not None else ["Be concise", "Act biologically"]
        self.tasks_attempted = 0
        self.tasks_correct = 0

    def mutate(self):
        # Mutate temperature
        if random.random() < MUTATION_RATE_TEMP:
            self.temp += random.uniform(-0.05, 0.05)
            self.temp = max(0.1, min(1.0, self.temp))
            
        # Mutate heuristics
        if random.random() < MUTATION_RATE_HEURISTIC:
            action = random.choice(["add", "remove", "modify"])
            if action == "add":
                new_heuristics = ["Think step-by-step", "Use minimal words", "Prioritize accuracy", "Work backwards", "Be brief", "Code exactly"]
                self.heuristics.append(random.choice(new_heuristics))
            elif action == "remove" and len(self.heuristics) > 1:
                self.heuristics.pop(random.randrange(len(self.heuristics)))
            elif action == "modify" and len(self.heuristics) > 0:
                idx = random.randrange(len(self.heuristics))
                modifications = {"Be concise": "Answer with minimal words", "Act biologically": "Conserve energy above all"}
                if self.heuristics[idx] in modifications:
                    self.heuristics[idx] = modifications[self.heuristics[idx]]
        
        # Deduplicate heuristics silently
        self.heuristics = list(set(self.heuristics))

# --- EVOLUTION ENGINE ---
class EvolutionEngine:
    def __init__(self):
        self.evaluator = FuzzyEvaluator("phase30/tasks.json")
        self.client = OllamaClient()
        self.metrics = []
        
        if RUN_BASELINE:
            print("--- RUNNING RAW GEMINI BASELINE ---")
            self.population = [Agent(i, temp=0.7, heuristics=[]) for i in range(POPULATION_SIZE)]
        else:
            self.population = [Agent(i) for i in range(POPULATION_SIZE)]

    async def evaluate_agent(self, agent, task, gen_id):
        # Prompt Isolation -> Evaluation happens OUTSIDE the prompt.
        if RUN_BASELINE:
            prompt = f"Solve the task: {task['task']}"
        else:
            h_str = ", ".join(agent.heuristics)
            prompt = f"You are MONO agent Gen {gen_id}.\nHeuristics: {h_str}\nEnergy: {agent.energy}.\n\nSolve the task:\n{task['task']}"
            
        response = await self.client.generate(prompt=prompt, model=None)
        
        # Check for errors in response
        if "[SYSTEM ERROR]" in response or "[OLLAMA ERROR]" in response:
            print(f"  Task {task.get('id')} -> FAILED: {response}")
            
        score = self.evaluator.evaluate(response, task["expected_keywords"])
        
        # Apply score to energy
        agent.energy += score
        agent.tasks_attempted += 1
        if score == 15:
            agent.tasks_correct += 1
        elif score == 5:
            # print(f"  Task {task.get('id')} -> PARTIAL (Keywords: {task['expected_keywords']})")
            pass
        elif score == -5:
             # print(f"  Task {task.get('id')} -> WRONG")
             pass
            
        return score

    def tournament_selection(self):
        # Pick 3 random agents, reproduce the best one
        candidates = random.sample(self.population, min(3, len(self.population)))
        best = max(candidates, key=lambda x: x.energy)
        
        # Create child
        child = Agent(len(self.population), temp=best.temp, heuristics=best.heuristics.copy())
        child.mutate()
        return child

    async def run_generation(self, gen_id):
        print(f"\n--- Generation {gen_id} ---")
        
        # Assign tasks
        tasks_pool = random.sample(self.evaluator.tasks, TASKS_PER_GENERATION)
        
        # Evaluate all agents
        total_tasks = len(self.population) * len(tasks_pool)
        completed_tasks = 0
        
        async def evaluate_with_progress(agent, task, gid):
            nonlocal completed_tasks
            res = await self.evaluate_agent(agent, task, gid)
            completed_tasks += 1
            print(f"\r  Progress: {completed_tasks}/{total_tasks} tasks evaluated...", end="", flush=True)
            return res

        tasks_awaiting = []
        for agent in self.population:
            for task in tasks_pool:
                tasks_awaiting.append(evaluate_with_progress(agent, task, gen_id))
                
        print(f"Evaluating {total_tasks} tasks via Ollama (Parallel)...")
        await asyncio.gather(*tasks_awaiting)
        print() # New line after carriage return progress

        # Logging stats before selection
        total_attempts = sum(a.tasks_attempted for a in self.population)
        total_correct = sum(a.tasks_correct for a in self.population)
        success_rate = total_correct / total_attempts if total_attempts > 0 else 0
        avg_energy = sum(a.energy for a in self.population) / len(self.population)
        
        all_heuristics = []
        for a in self.population:
            all_heuristics.extend(a.heuristics)
            
        freq = {}
        for h in all_heuristics: freq[h] = freq.get(h, 0) + 1
        sorted_heuristics = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        dominant = [h[0] for h in sorted_heuristics]
        
        metric = {
            "generation": gen_id,
            "success_rate": success_rate,
            "avg_energy": avg_energy,
            "dominant_heuristics": dominant,
            "population_size": len(self.population)
        }
        self.metrics.append(metric)
        
        print(f"Gen {gen_id} -> Success: {success_rate:.2f} | Avg Energy: {avg_energy:.2f}")
        print(f"Dominant Heuristics: {dominant}")

        # Check Extinction
        alive_agents = [a for a in self.population if a.energy > 0]
        if not alive_agents:
            print("\n!!! EXTINCTION EVENT. All agents have died. !!!")
            return False

        if RUN_BASELINE:
             # Just reset tasks, no evolution
             for a in self.population:
                 a.tasks_attempted = 0
                 a.tasks_correct = 0
             return True
             
        # Selection & Reproduction (Kill bottom 50%, replace with tournament children)
        self.population.sort(key=lambda x: x.energy, reverse=True)
        survivors_count = len(self.population) // 2
        
        new_population = self.population[:survivors_count]
        
        while len(new_population) < POPULATION_SIZE:
            child = self.tournament_selection()
            new_population.append(child)
            
        self.population = new_population
        
        # Reset task counters for next gen
        for a in self.population:
            a.tasks_attempted = 0
            a.tasks_correct = 0
            
        return True

    async def run(self):
        generations_to_run = 1 if RUN_BASELINE else GENERATIONS
        try:
            for g in range(generations_to_run):
                alive = await self.run_generation(g)
                
                # Save incremental metrics
                filename = "phase30/baseline_metrics.json" if RUN_BASELINE else "phase30/phase30_metrics.json"
                with open(filename, "w") as f:
                    json.dump(self.metrics, f, indent=2)
                
                if not alive:
                    break
        finally:
            await self.client.close()
                
        print(f"\nFinal metrics saved to {filename}")

if __name__ == "__main__":
    engine = EvolutionEngine()
    asyncio.run(engine.run())
