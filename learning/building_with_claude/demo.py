from dotenv import load_dotenv
from anthropic import Anthropic
load_dotenv()


client = Anthropic()
model = "claude-sonnet-4-0"
messages = []
system_prompt = "Think yourself as well educated research analyst and find the answers of the below "

def add_user_message(messages , text):
    user_message = {"role" : "user" , "content" : text}
    messages.append(user_message)

def add_assistant_message(messages , text):
    assistant_message = {"role" : "assistant" , "content" : text}
    messages.append(assistant_message)

def chat(messages):
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
        temperature=1.0
    )

    return message.content[0].text

# Add the initial user question
add_user_message(messages , "how's the weather today?")

# Get Claude's response
answer = chat(messages)

# Add Claude's response to the conversation history
add_assistant_message(messages , answer)

# add follow up question 
add_user_message(messages , "what is the exact temperature?")

# Get the follow-up response with full context
final_answer = chat(messages)

#Temperature
# add temperature to claude api call to get more creative and dynamic answers

add_user_message(messages , "Write a one movie idea into one line")

movie_answer = chat(messages)

print(movie_answer)