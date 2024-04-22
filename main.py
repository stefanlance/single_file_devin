import anthropic
import json
import subprocess

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)

filename = "is_prime.py"

read_file = open(f"data/{filename}", "r")
file_contents = read_file.read()

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


def call_anthropic_api(system_prompt, user_prompt, tools_prompt):
    message = client.beta.tools.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0,
        tools=[tools_prompt],
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
    #print(response_string)
    response_json = json.loads(response_string)["content"][0]["input"]

    #print(response_json)

    return response_json

user_prompt = f"""
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

def handle_test_output(test_output):
    print(test_output)
    if test_output.returncode == 0:
        print("Tests passed successfully!")
        return None

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
    Your output should only include the json that was specified above.  
    Do not include any other content in your output.
    ONLY RETURN VALID JSON! MAKE SURE YOUR NEWLINES ARE ESCPAED CORRECTLY.
    """

    return call_anthropic_api(system_prompt, error_correcting_user_prompt, error_correction_command_tool)


def run_tests(test_command):
    test_output = run_test(test_command)
    error_correction_response_json = handle_test_output(test_output)
    if error_correction_response_json is not None:
        print(error_correction_response_json)
        error_correction_command = error_correction_response_json["command"]
        error_correction_output = subprocess.run(error_correction_command, shell=True)
        run_tests(test_command)
        
actual_response_json = call_anthropic_api(system_prompt, user_prompt, write_tests_tool)

new_file_contents = actual_response_json["file_contents"]
test_command = actual_response_json["test_command"]

new_filename = f"new_{filename}"

new_file = open(f"data/{new_filename}", "w")
new_file.write(new_file_contents)
new_file.close()
# Replace filename with new_filename in the test command
test_command = test_command.replace(filename, f"data/{new_filename}")

run_tests(test_command)
