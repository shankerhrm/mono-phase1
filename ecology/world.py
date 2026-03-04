import random
from typing import List
import math
from mono import MonoCell
from cell.lifecycle import cycle

class ResourceZone:
    def __init__(self, zone_id: int, max_resources: float, regen_rate: float):
        self.zone_id = zone_id
        self.max_resources = max_resources
        self.regen_rate = regen_rate
        self.current_resources = max_resources
        self.organisms: List[MonoCell] = []
        
    def regenerate(self):
        self.current_resources = min(self.max_resources, self.current_resources + self.regen_rate)
        
    def get_density(self) -> float:
        """Returns the ratio of current resources to max resources to indicate local resource density."""
        if self.max_resources <= 0:
            return 0.0
        return self.current_resources / self.max_resources

class EcologyWorld:
    def __init__(self, num_zones: int, max_resources_per_zone: float, regen_rate: float):
        self.zones = [ResourceZone(i, max_resources_per_zone, regen_rate) for i in range(num_zones)]
        self.cycle_count = 0
        
    def add_organism(self, cell: MonoCell, zone_id: int = None):
        if zone_id is None:
            zone_id = random.randint(0, len(self.zones) - 1)
        self.zones[zone_id].organisms.append(cell)
        
    def tick(self):
        self.cycle_count += 1
        all_survivors = []
        all_children = []
        
        for zone in self.zones:
            zone.regenerate()
            
            # Interference via Latency Shadowing
            # Crowding introduces an indirect penalty: delay scaled by number of competing organisms
            crowding_penalty = max(0.0, (len(zone.organisms) - 1) * 0.1)
            
            # Temporarily apply crowding penalty to calculate functional tau
            for cell in zone.organisms:
                cell.delay += crowding_penalty
                
            # Resource Competition Mechanism
            # Order access by tau_organism (lowest/fastest gets first access)
            zone.organisms.sort(key=lambda c: c.get_tau_organism())
            
            next_gen_zone = []
            
            local_density = zone.get_density()
            
            for cell in zone.organisms:
                if cell.structure.size() <= 0:
                    continue # Dead
                
                # Try to consume resources based on cell base intake, but don't eat more than can be stored
                energy_deficit = cell.id.E_m - cell.energy.E
                desired_intake = min(cell.id.E_i, max(0.0, energy_deficit))
                
                actual_intake = 0.0
                if zone.current_resources >= desired_intake:
                    zone.current_resources -= desired_intake
                    actual_intake = desired_intake
                else:
                    actual_intake = zone.current_resources
                    zone.current_resources = 0.0
                
                # cycle the cell
                death_reason, log, child = cycle(
                    cell,
                    resource_intake=actual_intake,
                    resource_structure=0.0,
                    local_resource_density=local_density,
                )
                
                # Remove temporary crowding penalty
                cell.delay -= crowding_penalty
                
                if child is not None:
                    all_children.append(child)

                if isinstance(death_reason, str):
                    with open("death_log.txt", "a") as f:
                        f.write(f"Cycle {self.cycle_count}, cell {cell.cell_id} died of {death_reason}. E: {cell.energy.E:.2f}, S: {cell.structure.size():.2f}\n")
                    with open(f"failed_cell_{cell.cell_id}.json", "w") as f:
                        import json
                        json.dump(list(cell.history)[-50:], f, indent=4)
                else:
                    if cell.structure.size() > 0:
                        next_gen_zone.append(cell)
                        all_survivors.append(cell)
                    
            zone.organisms = next_gen_zone
            
        return all_survivors, all_children
