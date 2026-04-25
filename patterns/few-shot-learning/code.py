import instructor
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import numpy as np

client = instructor.patch(OpenAI())

class Example(BaseModel):
    input_text: str
    output_text: str

class DynamicFewShotSelector:
    def __init__(self, embeddings_client, examples: List[Example], k: int = 3):
        self.examples = examples
        self.k = k
        self.embeddings_client = embeddings_client
        self.example_embeddings = None
    
    async def get_embedding(self, text: str) -> list:
        response = await self.embeddings_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def initialize(self):
        self.example_embeddings = []
        for ex in self.examples:
            emb = await self.get_embedding(ex.input_text)
            self.example_embeddings.append(emb)
    
    async def select_examples(self, query: str) -> List[Example]:
        if self.example_embeddings is None:
            await self.initialize()
        
        query_embedding = await self.get_embedding(query)
        
        similarities = []
        for i, ex_emb in enumerate(self.example_embeddings):
            similarity = np.dot(query_embedding, ex_emb)
            similarities.append((similarity, i))
        
        similarities.sort(reverse=True)
        selected_indices = [i for _, i in similarities[:self.k]]
        
        selected = [self.examples[i] for i in selected_indices]
        return selected

class FewShotLearner:
    def __init__(self, examples: List[Example]):
        self.examples = examples
    
    def build_prompt(self, query: str) -> str:
        examples_text = "\n\n".join([
            f"Input: {ex.input_text}\nOutput: {ex.output_text}"
            for ex in self.examples
        ])
        
        return f"""Given the following examples of the desired input-output pattern:

{examples_text}

Now complete this new input:

Input: {query}
Output:"""
    
    async def complete(self, query: str, model: str = "gpt-4o") -> str:
        prompt = self.build_prompt(query)
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You follow the pattern shown in examples exactly."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

async def dynamic_example_selection():
    examples_pool = [
        Example(input_text="Translate 'hello' to Spanish", output_text="hola"),
        Example(input_text="Translate 'goodbye' to Spanish", output_text="adiós"),
        Example(input_text="Translate 'thank you' to Spanish", output_text="gracias"),
        Example(input_text="Translate 'please' to Spanish", output_text="por favor"),
        Example(input_text="Translate 'hello' to French", output_text="bonjour"),
        Example(input_text="Translate 'goodbye' to French", output_text="au revoir"),
    ]
    
    selector = DynamicFewShotSelector(client, examples_pool, k=2)
    selected = await selector.select_examples("Translate 'thank you' to French")
    
    learner = FewShotLearner(selected)
    result = await learner.complete("Translate 'please' to French")
    
    return result