from enum import Enum
import anthropic
import html
import json
import subprocess
from typing import List, Dict
import os

# https://pypi.org/project/llm-claude/
# 

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)

task_type_enum_values = ['SUGGEST_IMPROVEMENTS', 
                         'WRITE_TESTS', 
                         'RUN_TESTS', 
                         'FIX_BUG']

suggestable_task_type_enum_values = ['WRITE_TESTS', 'FIX_BUG']

suggest_improvements_tool = {
    "name": "suggest_improvements",
    "description": "Suggest one type of improvement to the given Python file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "string",
                "description": "The contents of the Python file.  Must be a single-line that is properly escaped."
            },
            "suggested_improvement_type": {
                "type": "string",
                "enum": suggestable_task_type_enum_values,
                "description": "The suggested improvement type to the Python file."
            },
            "explanation": {
                "type": "string",
                "description": "The explanation for the suggested improvement."
            },
        },
        "required": ["file_contents", "suggested_improvement_type", "explanation"],
    }
}

write_tests_tool = {
    "name": "create_file_with_tests",
    "description": "Add tests to the given Python file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "string",
                "description": "The contents of the Python file.  Must be a single-line that is properly escaped."
            },
            "test_command": {
                "type": "string",
                "description": "The Pytest command to run the tests from the CLI."
            },
        },
        "required": ["file_contents", "test_command"]
    }
}


def call_anthropic_api(system_prompt, user_prompt, tools_prompts : List[Dict]):
    message = client.beta.tools.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0,
        tools=tools_prompts,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    }
                ]
            }
        ]
    )

    response_string = message.model_dump_json()
    print(response_string)

    for response_item in json.loads(response_string)["content"]:
        if "input" not in response_item:
            continue

        response_json = response_item["input"]
        return response_json
    
    return None

def suggest_improvements_prompt(filename, file_contents):
    return f"""
    The following code is a single-file Python project named '{filename}'.  
    There may be some issues with the code that you can identify and suggest 
    improvements for.  Please return the full file with the implementation 
    and one suggested improvement.  Please also provide a brief explanation 
    of why you made the change you did.  Please return your output in the 
    `suggest_improvements_tool` tool.
    Here are the contents of the file:
    {{
        {json.dumps(file_contents)},
    }}
    Your output should only include the json that was specified above.  
    Do not include any other content in your output.
    ONLY RETURN VALID JSON! MAKE SURE YOUR NEWLINES ARE ESCPAED CORRECTLY.
    """

def run_tests_prompt(filename, file_contents):
    return f"""
    The following code is a single-file Python project named '{filename}'.  
    There may or may not be tests for the methods in the file.  If there are 
    any gaps in any kind of relevant test coverage, please write tests using
    the Pytest framework, and 
    return the full file with the implementation and the tests.  Please also 
    provide a pytest command that will run all the tests you wrote. 
    Please return your output in the `create_file_with_tests` tool.
    Here are the contents of the file:
    {{
        {json.dumps(file_contents)},
    }}
    Your output should only include the json that was specified above.  
    Do not include any other content in your output.
    ONLY RETURN VALID JSON! MAKE SURE YOUR NEWLINES ARE ESCPAED CORRECTLY.
    """

system_prompt = """
You are an expert Python software engineer with decades of experience in 
many types of projects, both big and small.  You are opinionated, very 
familiar with common libraries, always use standard Python idioms, and 
always test your code.  Your code is used as reference material by many 
engineers.
"""


# TODO containize this or sanitize the test so that we don't accidentally
# remove files or do something malicious
def run_test(test_command):
    test_output = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    return test_output

error_correction_command_tool = {
    "name": "write_error_correction_command",
    "description": "Return a command that corrects an error encountered when running tests with pytest.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The CLI command to run to correct the test failure."
            },
            "error_reason": {
                "type": "string",
                "description": "The reason the error occurred."
            },
        },
        "required": ["command", "error_reason"]
    }
}

bug_fix_tool = {
    "name": "bug_fix_file_contents",
    "description": "Return updated file contents to fix error while running tests.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_contents": {
                "type": "string",
                "description": "The updated file contents as a single-line double-escaped string."
            },
            "error_reason": {
                "type": "string",
                "description": "The reason the error occurred."
            },
        },
        "required": ["file_contents", "error_reason"]
    }
}

def handle_test_output(filename, test_output):
    print(test_output)
    if test_output.returncode == 0:
        print("Tests passed successfully!")
        return None

    read_file = open(f"{filename}", "r")
    file_contents = read_file.read()
    read_file.close()
    error = test_output.stderr
    error_correcting_user_prompt = f"""
    The tests failed to pass.  Here is the error that was returned when
    we ran the tests:
    {{
        "error": "{error}"
    }}
    If the tests did not run, and the error is due to missing dependencies,
    please give us a pip3 command that will install the necessary dependencies.
    Use the `write_error_correction_command` tool to return the command.

    Otherwise, if the tests run and the error is due to one or more tests failing,
    then examine the contents of the file provided below to check whether the
    error is because of a bug in the source file or because of an incorrect test.
    Use the `bug_fix_file_contents` tool to return the updated file contents
    such that the error no longer occurs and all the tests pass.
    {{
        "file_contents": "{file_contents}"
    }}

    Your output should only include the string that was specified above.  
    Do not include any other content in your output.
    """

    return call_anthropic_api(system_prompt, error_correcting_user_prompt, 
                              [error_correction_command_tool, bug_fix_tool])


TaskType = Enum('TaskType', task_type_enum_values)

class Task:
    def __init__(self, type : TaskType, command : str = '') -> None:
        self.type = type
        self.command = command

def do_tasks(filename : str, file_contents : str, tasks : List[Task]):
    filename = "data/" + filename

    while tasks:
        current_task = tasks.pop()
        match current_task.type:
            case TaskType.SUGGEST_IMPROVEMENTS:
                # Call API with suggest improvements prompt
                actual_response_json = call_anthropic_api(system_prompt, suggest_improvements_prompt(filename, file_contents), [suggest_improvements_tool])
                new_file_contents = actual_response_json["file_contents"].encode("utf-8").decode("unicode_escape")
                new_file_contents = html.unescape(new_file_contents)
                print(new_file_contents)
                new_file = open(f"{filename}", "w")
                new_file.write(new_file_contents)
                new_file.close()
                # Read the suggestion.
                # If the suggestion is to write tests, push WRITE_TESTS task
                # If the suggestion is to fix a bug, push FIX_BUG task
                task_type = TaskType[actual_response_json["suggested_improvement_type"]]
                print(actual_response_json["explanation"])
                if task_type == TaskType.FIX_BUG and not current_task.command:
                    new_task = Task(TaskType.WRITE_TESTS)
                    tasks.append(new_task)
                else:
                    new_task = Task(task_type, current_task.command)
                    tasks.append(new_task)
                
                
            case TaskType.WRITE_TESTS:
                # Call API with write tests prompt
                actual_response_json = call_anthropic_api(system_prompt, run_tests_prompt(filename, file_contents), [write_tests_tool])
                new_file_contents = actual_response_json["file_contents"].encode("utf-8").decode("unicode_escape")
                new_file_contents = html.unescape(new_file_contents)
                print(new_file_contents)
                test_command = actual_response_json["test_command"]

                # Write output to file
                new_file = open(f"{filename}", "w")
                new_file.write(new_file_contents)
                new_file.close()

                # Push RUN_TESTS task
                new_task = Task(TaskType.RUN_TESTS, test_command)
                tasks.append(new_task)

            case TaskType.RUN_TESTS:
                test_output = run_test(current_task.command)
                error_correction_response_json = handle_test_output(filename, test_output)
                
                if error_correction_response_json is None:
                    continue

                print(error_correction_response_json)

                if "command" in error_correction_response_json:
                    error_correction_command = error_correction_response_json["command"]
                    new_task = Task(TaskType.FIX_BUG, error_correction_command)
                    tasks.append(new_task)
                elif "file_contents" in error_correction_response_json:
                    new_file_contents = error_correction_response_json["file_contents"].encode("utf-8").decode("unicode_escape")
                    new_file_contents = html.unescape(new_file_contents)
                    new_file = open(f"{filename}", "w")
                    new_file.write(new_file_contents)
                    new_file.close()

                    new_task = Task(TaskType.RUN_TESTS, test_command)
                    tasks.append(new_task)

            case TaskType.FIX_BUG:
                _ = subprocess.run(current_task.command, shell=True)
                new_task = Task(TaskType.RUN_TESTS)
                tasks.append(new_task)

    return

def set_up_files(filename): 
    if os.path.exists(f"data/original_{filename}"):
        read_file = open(f"data/original_{filename}", "r")
        file_contents = read_file.read()
        read_file.close()
        write_file = open(f"data/{filename}", "w")
        write_file.write(file_contents)
        write_file.close()

    read_file = open(f"data/{filename}", "r")
    file_contents = read_file.read()
    read_file.close()

    if not os.path.exists(f"data/original_{filename}"):
        write_file = open(f"data/original_{filename}", "w")
        write_file.write(file_contents)
    
    return file_contents

if __name__ == "__main__":
    filename = "is_prime.py"
    file_contents = set_up_files(filename)

    tasks = [Task(TaskType.SUGGEST_IMPROVEMENTS)]
    do_tasks(filename, file_contents, tasks)
