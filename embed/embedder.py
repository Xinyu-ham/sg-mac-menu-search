from openai import OpenAI

class Embedder:
    def __init__(self, openai_client: OpenAI, embedding_model: str):
        self.embedding_model = embedding_model
        self.client = openai_client

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        if isinstance(text, str):
            return response.data[0].embedding
        else:
            return [r.embedding for r in response.data]