# Load env variables and create client
from dotenv import load_dotenv
from anthropic import Anthropic
import json
import re
import ast
from statistics import mean


load_dotenv()

client = Anthropic()
model = "claude-haiku-4-5"

# Helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def chat(messages, system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences,
    }

    if system:
        params["system"] = system

    message = client.messages.create(**params)
    return message.content[0].text


## Process to generate dataset of test cases using claude

def generate_dataset():
    prompt = """
        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
                "format" : Python or JSON or Regex,
                "solution_criteria" : Include solution criteria to evaluate the output
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code

        Please generate 3 objects.
    """

    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequences=["```"])
    return json.loads(text)


dataset = generate_dataset()
# print("dataset" , dataset)

with open('dataset.json', 'w') as f:
    json.dump(dataset, f, indent=2)


## work with dataset of test cases

def run_prompt(test_case):
    prompt= f"""
    Please solve the following task

    {test_case["task"]}

    generate only Python or JSON or Plain regex
    Do not add any commentry or unnecessary explaination
    """
    messages = []
    add_user_message(messages , prompt)
    output = chat(messages)
    return output

## Give Grade by model 
def grade_by_model(test_case , output):
    eval_prompt = f"""
        You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

        Original Task:
        <task>
        {test_case["task"]}
        </task>

        Solution to Evaluate:
        <solution>
        {output}
        </solution>

        <criteria>
        {test_case["solution_criteria"]}
        </criteria>
        
        Output Format
        Provide your evaluation as a structured JSON object with the following fields, in this specific order:
        - "strengths": An array of 1-3 key strengths
        - "weaknesses": An array of 1-3 key areas for improvement
        - "reasoning": A concise explanation of your overall assessment
        - "score": A number between 1-10

        Respond with JSON. Keep your response concise and direct.
        Example response shape:
        {{
            "strengths": string[],
            "weaknesses": string[],
            "reasoning": string,
            "score": number
        }}
    """

    messages = []
    add_user_message(messages , eval_prompt)
    add_assistant_message(messages, "```json")
    
    eval_text = chat(messages, stop_sequences=["```"])
    return json.loads(eval_text)


# Functions to validate the output structure
def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(response, test_case):
    format = test_case["format"]
    if format == "json":
        return validate_json(response)
    elif format == "python":
        return validate_python(response)
    else:
        return validate_regex(response)


def run_test_case(test_case):
    """Calls run_prompt, then grades the result"""
    output = run_prompt(test_case)
    
    model_grade = grade_by_model(test_case , output)
    print("model_grade" , model_grade)

    model_score = model_grade["score"]
    reasoning = model_grade["reasoning"]

    syntax_score = grade_syntax(output , test_case)

    score = (model_score + syntax_score) / 2
        
    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }


def run_eval(dataset):
    """Loads the dataset and calls run_test_case with each case"""
    results = []
    
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)
    
    average_score = mean([result["score"] for result in results])
    print(f"Average score: {average_score}")

    return results

## send data to run_eval to start the process
with open("dataset.json" , "r") as f:
    dataset = json.load(f)

results = run_eval(dataset)


print(json.dumps(results, indent=2))