from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-0"
messages = []

def user_messages(messages, text):
    user = {"role": "user", "content": text}
    messages.append(user)

def ai_messages(messages, text):
    ai = {"role": "assistant", "content": text}
    messages.append(ai)

def chat(messages):
    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages
    )
    return response.content[0].text

while True:

    user_input = input('> ')

    print("user_input" , user_input)

    user_messages(messages , user_input)

    answer = chat(messages)

    print("answer" , answer)

    ai_messages(messages , answer)

    print(messages)