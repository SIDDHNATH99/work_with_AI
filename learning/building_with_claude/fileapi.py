# Load env variables and create client
from dotenv import load_dotenv
from anthropic import Anthropic
from pathlib import Path
from anthropic.types import Message


load_dotenv()

client = Anthropic(
    default_headers={
        "anthropic-beta": "code-execution-2025-08-25, files-api-2025-04-14"
    }
)
model = "claude-sonnet-4-5-20250929"

# Helper functions
def add_user_message(messages, message):
    user_message = {
        "role": "user",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    assistant_message = {
        "role": "assistant",
        "content": message.content if isinstance(message, Message) else message,
    }
    messages.append(assistant_message)


def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    thinking=False,
    thinking_budget=2000,
):
    params = {
        "model": model,
        "max_tokens": 10000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if thinking:
        params["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget,
        }

    if tools:
        params["tools"] = tools

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message


def text_from_message(message):
    return "\n".join([block.text for block in message.content if block.type == "text"])


def upload(file_path):
    path = Path(file_path)
    extension = path.suffix.lower()

    mime_type_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/plain",
        ".py": "text/plain",
        ".js": "text/plain",
        ".html": "text/plain",
        ".css": "text/plain",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xml": "application/xml",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    mime_type = mime_type_map.get(extension)

    if not mime_type:
        raise ValueError(f"Unknown mimetype for extension: {extension}")
    filename = path.name

    with open(file_path, "rb") as file:
        return client.beta.files.upload(file=(filename, file, mime_type))


def list_files():
    return client.beta.files.list()


def delete_file(id):
    return client.beta.files.delete(id)


def download_file(id, filename=None):
    file_content = client.beta.files.download(id)

    if not filename:
        file_metadata = get_metadata(id)
        file_content.write_to_file(file_metadata.filename)
    else:
        file_content.write_to_file(filename)


def get_metadata(id):
    return client.beta.files.retrieve_metadata(id)

file_metadata = upload("streaming.csv")

messages = []

add_user_message(
    messages,
    [
        {
            "type": "text",
            "text": """
Run a detailed analysis to determine major drivers of churn.
Your final output should include at least one detailed plot summarizing your findings.

Critical note: Every time you execute code, you're starting with a completely clean slate. 
No variables or library imports from previous executions exist. You need to redeclare/reimport all variables/libraries.
            """,
        },
        {"type": "container_upload", "file_id": file_metadata.id},
    ],
)

chat(messages, tools=[{"type": "code_execution_20250825", "name": "code_execution"}])

download_file("file_011CPYZqxoMSsfbrSzFw8j9X")