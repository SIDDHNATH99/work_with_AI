from dotenv import load_dotenv
from anthropic import Anthropic
load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-0"
messages = []

def add_user_message(messages , text):
    user_message = {"role" : "user" , "content" : text}
    messages.append(user_message)

def add_assistant_message(messages , text):
    assistant_message = {"role" : "assistant" , "content" : text}
    messages.append(assistant_message)

def chat(messages , stop_sequences):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        temperature=1.0,
        stop_sequences=stop_sequences
    )

    return message.content[0].text

# add_user_message(messages , "Generate a very short event bridge rule as json")

add_user_message(messages , "Generate three different sample AWS CLI commands. Each should be very short")

add_assistant_message(messages , ("```bash"))

text = chat(messages, stop_sequences=["```"])
# text = chat(messages)

print(text)

## Exercise 2
