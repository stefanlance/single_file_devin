from enum import Enum
import anthropic
import html
import json
import subprocess
from typing import List, Dict, Tuple
import os


client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    #api_key="my_api_key",
)

write_program_tool = {
    "name": "write_program_tool",
    "description": "Write a program I ask you to write",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "string",
                "description": f"""The contents of the Python file. 
                  Must be valid Python syntax."""
            },
        },
        "required": ["file_contents"],
    }
}


#print(message.content)
#print(message.model_dump_json())
# print("MESSAGE BEFORE DOING ANYTHING")
# print("--------------------------------------------------")
# print(message)
# print("--------------------------------------------------")
# resp_json = message.model_dump_json()
# print("JSON AFTER MODEL_DUMP_JSON")
# print("--------------------------------------------------")
# print(resp_json)
# print("--------------------------------------------------")
# to_json = message.to_json()
# print("JSON AFTER TO_JSON")
# print("--------------------------------------------------")
# print(to_json)
# print("--------------------------------------------------")
# loads = json.loads(resp_json)["content"]
# print("JSON AFTER LOADS")
# print("--------------------------------------------------")
# print(loads)
# #print(loads)

# # Print json.dumps of is_prime.py
# # read is_prime.py
# is_prime_py = open("data/is_prime.py", "r")
# is_prime_py_contents = is_prime_py.read()
# print("--------------------------------------------------")
# print("JSON_DUMPS IS_PRIME.PY")
# print("--------------------------------------------------")
# print(json.dumps(is_prime_py_contents))
# print("--------------------------------------------------")
# is_prime_py.close()

# # Write json.dumps of is_prime.py to is_prime.json
# is_prime_json = open("data/is_prime.json", "w")
# is_prime_json.write(json.dumps(is_prime_py_contents))
# is_prime_json.close()

# # Write json.loads(json.dumps(is_prime.py)) to loads_is_prime.py
# loads_is_prime = json.loads(json.dumps(is_prime_py_contents))
# print("--------------------------------------------------")
# print("JSON_LOADS IS_PRIME.PY")
# print("--------------------------------------------------")
# print(loads_is_prime)
# print("--------------------------------------------------")
# loads_is_prime_py = open("data/loads_is_prime.py", "w")
# loads_is_prime_py.write(loads_is_prime)
# loads_is_prime_py.close()


response_with_text_field = None
# Read from test_response.txt
with open("test_response.txt", "r") as file:
    response_with_text_field = file.read()
    file.close()

message = client.beta.tools.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    temperature=0,
    system=f"""You are an expert Python software engineer with decades 
    of experience in many types of projects, both big and small.  
    You are opinionated, very familiar with common libraries, always 
    use standard Python idioms, and always test your code.  Your code 
    is used as reference material by many engineers.""",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
                    Please check the format of the python program that is included in this string.
                    Please return only the contents of the file, and nothing else, in a format
                    such that it can be saved to a file with no formatting issues.  Please ensure
                    that all characters that need to be escaped, are escaped exactly once. Keep
                    in mind that some characters may already be escaped, and if so, you should
                    not double-escape them. 
                    For example, if the string 'foo\\n\"bar\"' appears in the file, you should replace it with
                    'foo\\n\\"bar\\"'. 
                    This is the file contents:
                    {response_with_text_field}""",
                }
            ]
        }
    ],
    #tools=[],
)
print(message.model_dump_json())