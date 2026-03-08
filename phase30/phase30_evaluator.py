import json

class FuzzyEvaluator:
    def __init__(self, tasks_file="phase30/tasks.json"):
        with open(tasks_file, "r") as f:
            self.tasks = json.load(f)
            
    def get_task(self, task_id):
        for t in self.tasks:
            if t["id"] == task_id:
                return t
        return None
        
    def evaluate(self, response: str, expected_keywords: list) -> int:
        """
        Fuzzy evaluates the response.
        +15 for matching all keywords
        +5 for matching some keywords
        -5 for missing all keywords
        -10 if [API ERROR] or [SYSTEM ERROR] is explicitly in response
        """
        response_lower = response.lower()
        
        if "[api error]" in response_lower or "[system error]" in response_lower:
            return -10
            
        matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
        
        if matches == len(expected_keywords):
            return 15
        elif matches > 0:
            return 5
        else:
            return -5
