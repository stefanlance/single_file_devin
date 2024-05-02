# Project Overview

- Goal: simplified version of Devin
- Take a single file Python project
- Ask model to improve it (write tests, fix a bug, refactor)
- Tasks: financial calculator; is_prime; red black tree


# Brief Design Discussion

- Use a stack of tasks to manage control flow
- Each task asks the model to do something with the file and possibly the
  output of running tests
- Current set of tasks: suggest improvements, write tests, fix bug, refactor
- Example: WRITE_TESTS will ask the model to write tests and provide a command
  that we execute to run the tests.  If any tests fail, we push a FIX BUG
  task onto the stack and give the test output to the model.


# Instructions

```
$ python3 main.py <filename> <initial_task_name>
```

E.g.:
```
$ python3 main.py is_prime.py SUGGEST_IMPROVEMENTS
$ python3 main.py calculator.py REFACTOR
```


# Problems Encountered

- Marshaling and unmarshaling a Python file as JSON
- Specifying a JSON schema for the model to return its result in.
  Claude allows this with its beta client's input_schema field.
- Sonnet couldn't fix the RBT bug, so we tried to give it memory of
  previous requests and responses.  This exceeded the context window,
  so (we think) the API stopped trying to use the input_schema.  This made
  the API sometimes return in the text field (which is unstructured and thus
  hard to parse), and sometimes return in the input field (which is 
  structured JSON, and easy to parse).
- Opus is very slow and very expensive compared with Sonnet: 
  Rough numbers from our experience:
  Opus: 20-30 seconds and 3-6 cents per API call
  Sonnet: 5 seconds and < 1 cent per API call

# Future Work

- Reintroducing memory, but more carefully: bound it (e.g. only the most
  recent request and response, and/or condense the requests and responses)
- Give the model examples of inputs and outputs so that it would more
  likely use the given input_schema
- Figure out why Sonnet adds unnecessary unit tests