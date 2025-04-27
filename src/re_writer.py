import os
import openai
from dotenv import load_dotenv

class Rewriter:
    def __init__(self):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation = []
        self.model = "gpt-4-turbo"

    def clear_conversation(self):
        self.conversation = []

    def append_system_message(self, message):
        self.conversation.append({"role": "system", "content": message})

    def append_user_message(self, message):
        self.conversation.append({"role": "user", "content": message})

    def rewriter(self, model="gpt-4-turbo"):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to get response from OpenAI: {str(e)}")

    def analyze_text(self, text, prompt):
        try:
            self.clear_conversation()
            self.append_system_message(prompt)
            self.append_user_message(text)
            return self.rewriter(self.model)
        except Exception as e:
            raise Exception(f"Failed to analyze text: {str(e)}")
    