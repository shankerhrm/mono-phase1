import random

class Structure:
    def __init__(self, initial_size=0):
        self.graph = {}
        for i in range(initial_size):
            self.graph[i] = {'metadata': {'type': 'default', 'age': 0, 'utility': 0}, 'edges': {}}

    def size(self) -> int:
        return len(self.graph)

    def mutate(self, identity):
        if random.random() < identity.mutation_rate:
            node_id = len(self.graph)
            self.graph[node_id] = {'metadata': {'type': 'default', 'age': 0, 'utility': 0}, 'edges': {}}
            return 1
        return 0

    def reorganize(self, identity):
        # Placeholder for reorganization logic
        return 0

    def compress(self, identity):
        # Placeholder: remove a node if size > 0
        if self.graph:
            node_id = list(self.graph.keys())[0]
            del self.graph[node_id]
            return -1
        return 0

    def decay(self, decay_rate):
        to_remove = [node_id for node_id in list(self.graph.keys()) if random.random() < decay_rate]
        delta = -len(to_remove)
        for node_id in to_remove:
            del self.graph[node_id]
        return delta
