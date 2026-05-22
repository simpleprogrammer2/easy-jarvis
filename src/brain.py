import logging
from typing import Dict

class Brain:
    def __init__(self):
        self.memory: Dict = {}

    def store_memory(self, key: str, value: any):
        self.memory[key] = value

    def retrieve_memory(self, key: str) -> any:
        return self.memory.get(key)
