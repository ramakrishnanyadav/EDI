import os
import openai

client = openai.OpenAI(
    api_key="rc_c9ed81599646e29873ee8da73e9eb4d07cd97f0b37c2c015430b44bc56d47e7b",
    base_url="https://api.featherless.ai/v1"
)

try:
    models = client.models.list()
    print("Available models:")
    for m in models.data[:10]:
        print(f"- {m.id}")
except Exception as e:
    print(f"Error fetching models: {e}")
