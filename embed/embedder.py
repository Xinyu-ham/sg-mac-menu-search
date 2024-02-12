from openai import OpenAI

class Embedder:
    def __init__(self, model: str, api_key: str=''):
        self.model = model
        if not api_key:
            self.client = OpenAI()
        else:
            self.client = OpenAI(api_key)

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        if isinstance(text, str):
            return response.data[0].embedding
        else:
            return [r.embedding for r in response.data]