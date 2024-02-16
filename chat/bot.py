from openai import OpenAI

class UnidentifiableQuestionError(Exception):
    def __init__(self, question):
        self.question = question
        self.message = f'Could not identify question type for "{question}"'

class ChatBot:
    client: OpenAI
    model: str
    def __init__(self, openai_client: OpenAI, model: str='gpt-3.5-turbo'):
        self.client = openai_client
        self.model = model

    def indentify_question_type(self, question: str) -> str:
        transcript = Transcript()
        transcript.add_system_message(
            '''Classify user question into the following types: 1.asking about a specific product or 2.asking for recommendations. Respond with only the number, no texts or punctuations.''')
        transcript.add_user_message(question)

        retries = 3
        while retries:
            response = self.respond(transcript.messages)
            if response in ('1', '2'):
                return int(response) - 1
            retries -= 1
        raise UnidentifiableQuestionError(question)

    def respond(self, messages: str) -> str:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages
        ).choices[0].message.content
    
    def answer(self, question: str, name: str, description: str, price: float) -> str:
        transcript = Transcript()
        transcript.add_system_message('You are a support agent. Please respond to the user\'s question.')
        transcript.add_user_message(question)
        transcript.add_system_message(f'Use the following information - Product: {name}, Description: {description}, Price: S${price:,.2f}')
        return self.respond(transcript.messages)

class Transcript:
    def __init__(self, past_messages: list[tuple[str, str]] | None=None):
        if past_messages is None:
            past_messages = []
        self.past_messages = past_messages

    def add_system_message(self, message: str):
        self.past_messages.append(('system', message))

    def add_user_message(self, message: str):
        self.past_messages.append(('user', message))

    def __str__(self):
        return '\n'.join(f'[{source}] {message}' for source, message in self.past_messages)
    
    def __repr__(self):
        return '\n'.join(f'[{source}] {message}' for source, message in self.past_messages)
    
    def __len__(self):
        return len(self.past_messages)
    
    @property
    def messages(self) -> list[dict[str, str]]:
        return [{'role': source, 'content': message} for source, message in self.past_messages]