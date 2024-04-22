import anthropic
import json
import subprocess

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
)

filename = "is_prime.py"

read_file = open(f"data/{filename}", "r")
file_contents = read_file.read()

def call_anthropic_api(system_prompt, user_prompt):
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0,
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
    response_json = json.loads(response_string)["content"][0]["text"]

    actual_response_json = json.loads(response_json)

    return actual_response_json

user_prompt = f"""
The following code is a single-file Python project named '{filename}'.  
There may or may not be tests for the methods in the file.  If there are 
any gaps in any kind of relevant test coverage, please write tests using
the Pytest framework, and 
return the full file with the implementation and the tests.  Please also 
provide a pytest command that will run all the tests you wrote.  Your 
output should be in a single-line escaped JSON in this format:
{{
    "file_contents": "string",
    "test_command": "string"
}}
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

def handle_test_output(test_output):
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
    Your output should be a validly formatted json with this structure:
    {{
        "command": "string",
        "error_reason": "string"
    }}
    In the error_reason field, please explain why the error is occurring.
    ONLY RETURN VALID JSON! MAKE SURE YOUR NEWLINES ARE ESCPAED CORRECTLY.
    """

    return call_anthropic_api(system_prompt, error_correcting_user_prompt)


def run_tests(test_command):
    test_output = run_test(test_command)
    error_correction_response_json = handle_test_output(test_output)
    if error_correction_response_json is not None:
        error_correction_command = error_correction_response_json["command"]
        error_correction_output = subprocess.run(error_correction_command, shell=True)
        run_tests(test_command)
        
actual_response_json = call_anthropic_api(system_prompt, user_prompt)

new_file_contents = actual_response_json["file_contents"]
test_command = actual_response_json["test_command"]

new_filename = f"new_{filename}"

new_file = open(f"data/{new_filename}", "w")
new_file.write(new_file_contents)
new_file.close()
# Replace filename with new_filename in the test command
test_command = test_command.replace(filename, f"data/{new_filename}")

run_tests(test_command)
