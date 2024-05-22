from openai import OpenAI
from typing import List

class OpenAIClient:
    def __init__(self, model: str):
        self.client = OpenAI()
        self.model = model

    def generate_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.model, input=[text])
        return response.data[0].embedding
