from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-0"
messages = []

with client.messages.stream(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role" : "user",
            "content" : "write explaination about fake db in one liner"
        }
    ]
) as stream:
    for text in stream.text_stream:
        pass

final_message = stream.get_final_message()
print("final_message>" , final_message)


