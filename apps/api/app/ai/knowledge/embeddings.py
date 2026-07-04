"""
Nexus AI — Embedding Generator
Generates semantic embeddings using word-vector aggregation.
Ensures keyword overlaps correspond to higher cosine similarity scores.
"""
from __future__ import annotations
from typing import List
import hashlib
import random
import re

class EmbeddingGenerator:
    """Creates semantic-driven deterministic embeddings via bag-of-words summing."""
    
    def __init__(self, dimensions: int = 128):
        self.dimensions = dimensions

    def _get_word_vector(self, word: str) -> List[float]:
        """Generates a deterministic vector for a single word."""
        hasher = hashlib.md5(word.encode("utf-8"))
        seed = int(hasher.hexdigest(), 16) % (2**31 - 1)
        rng = random.Random(seed)
        vec = [rng.uniform(-1.0, 1.0) for _ in range(self.dimensions)]
        return vec

    def generate(self, text: str) -> List[float]:
        """Sums individual word vectors to create a combined normalized embedding."""
        words = re.findall(r"\w+", text.lower())
        if not words:
            # Fallback to random representation if text is empty
            words = ["default"]
            
        combined = [0.0] * self.dimensions
        for word in words:
            w_vec = self._get_word_vector(word)
            for i in range(self.dimensions):
                combined[i] += w_vec[i]
                
        # Normalize sum vector
        sq_sum = sum(x*x for x in combined)
        magnitude = sq_sum ** 0.5 if sq_sum > 0 else 1.0
        return [x / magnitude for x in combined]
