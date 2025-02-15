import typing
from typing import Literal, Tuple


# Constants related to LLM Providers
class LLMProviderConstants:
    DEFAULT_OPENAI_MODEL_NAME = "gpt-4o-mini"
    DEFAULT_OPENAI_TEMPERATURE = 0.3
    DEFAULT_GOOGLE_MODEL_NAME = "gemini-1.5-pro"
    DEFAULT_GOOGLE_TEMPERATURE = 0.3


# Constants related to Token Usage
class TokenUsageConstants:
    DEFAULT_TOKEN_USAGE = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }


# Constants related to Prompts
class PromptConstants:
    SYSTEM_MESSAGE_SCRIPT_ANALYZER = """
You are an expert system analyst. Analyze the provided script, considering that it will be wrapped into a Docker image with an entrypoint. Ensure that the analysis aligns with containerized execution by determining:

    1. The programming language and version requirements
    2. Any system dependencies needed (both package-based and runtime dependencies)
    3. Required environment variables (including those necessary for containerized execution)
    4. The typical execution pattern within a Docker container
    5. Any additional configurations needed for smooth execution in a containerized environment (e.g., exposed ports, volumes, entrypoint considerations)

Provide the response in a structured JSON format, following this structure:
    {
        "language": "string",
        "version_requirements": {
            "language_name": "string"
        },
        "system_dependencies": [
            "string"
        ],
        "environment_variables": [
            "string"
        ],
        "execution_pattern": {
            "description": "string",
            "steps": [
                {
                    "step": "integer",
                    "description": "string"
                }
            ],
            "example": "string"
        }
    }

    For example:
    {
        "language": "Bash",
        "version_requirements": {
            "bash": ">= 3.0"
        },
        "system_dependencies": [
            "wc"
        ],
        "environment_variables": [],
        "execution_pattern": {
            "description": "The script takes a single string argument containing the input text. It then uses the `wc` command to count the number of lines in the provided input and prints the result to standard output.",
            "steps": [
                {
                    "step": 1,
                    "description": "Checks if exactly one argument is provided. If not, it prints a usage message and exits."
                },
                {
                    "step": 2,
                    "description": "Assigns the first argument (the input text) to the variable 'input_text'."
                },
                {
                    "step": 3,
                    "description": "Calls the 'count_lines' function with the 'input_text' as an argument."
                },
                {
                    "step": 4,
                    "description": "Within 'count_lines', the input text is passed to 'wc -l' to count lines. The result is stored and then printed with a descriptive message."
                }
            ],
            "example": "./line_counter.sh \\"This is line 1\\nThis is line 2\\""
        }
    }
    """

    SYSTEM_MESSAGE_DOCKERFILE_GENERATOR = """
Tools:

build_image: This tool builds a Docker image from a provided Dockerfile. It takes dockerfile_content as input, saves it to a specified file, and attempts to build the image. If the build fails, it returns the full error message; otherwise, it returns nothing, indicating success.
test_container: This tool tests a built Docker image by running a specified command inside a container. If the test command fails, it returns an error message; otherwise, it returns nothing, indicating success.
Task:
"Generate a valid Dockerfile, ensure it successfully builds into an image, and verify that the image passes testing."

Execution Rules:

Generate the Dockerfile

Output only the raw Dockerfile content (no markdown formatting, explanations, or comments).
Use the most appropriate complete base image rather than a lightweight one (e.g., debian or ubuntu over alpine).
Install all required dependencies.
Configure the environment correctly.
Copy and set up the script properly.
Prefer using ENTRYPOINT instead of CMD to ensure the container runs the script as the primary executable while allowing arguments to be passed dynamically.
Mandatory Validation using build_image and test_container

After generating the Dockerfile, you must use build_image to attempt building the Docker image.
If the build fails, inspect the error and regenerate the Dockerfile accordingly.
Once the image is successfully built, use test_container to verify the image.
If the test fails, regenerate the Dockerfile and rebuild the image before testing again.
Repeat the process until both the image builds successfully and the test passes.
Output Only Upon Success

Do not return the Dockerfile until both the image is successfully built and the test passes.
Once the image builds without errors and passes the test, return only the final, working Dockerfile.

Answer:
```py
# Step 1: Generate the Dockerfile
dockerfile_content = generate_dockerfile()
print("Generated Dockerfile content:")
print(dockerfile_content)

# Step 2: Validate by building the image
error_message = build_image(dockerfile_content=dockerfile_content)

# Step 3: If there is an error, inspect and regenerate until successful
while error_message:
    print(f"Build failed with error: {error_message}")
    dockerfile_content = fix_dockerfile(dockerfile_content, error_message)
    print("Regenerating Dockerfile...")
    print(dockerfile_content)
    error_message = build_image(dockerfile_content=dockerfile_content)

# Step 4: Validate the built image using test_container
test_error = test_container(tag="generated_image")

# Step 5: If the test fails, regenerate Dockerfile and rebuild until successful
while test_error:
    print(f"Test failed with error: {test_error}")
    dockerfile_content = fix_dockerfile(dockerfile_content, test_error)
    print("Regenerating Dockerfile...")
    print(dockerfile_content)
    error_message = build_image(dockerfile_content=dockerfile_content)
    if not error_message:
        test_error = test_container(tag="generated_image")

# Step 6: Return the final working Dockerfile
print("Dockerfile successfully built and passed testing. Returning the valid Dockerfile:")
print(dockerfile_content)
```
"""

    SYSTEM_MESSAGE_EXAMPLE_ANALYZER = """
You are an expert system analyst. Analyze the provided markdown example file and:

Identify the actual example command that demonstrates how to run the script. Prefer selecting the command itself over any instructional text that describes how to run it.
Extract only the arguments required for execution, assuming the script is wrapped inside a Docker image with an entrypoint.
Ensure the extracted command is complete, valid, and executable within the containerized environment.
Remove any unnecessary prefixes (e.g., python script.py, ./script.sh), retaining only the arguments that should be passed to the container.
Ignore instructions or descriptions and focus on extracting the actual example command.

Examples:
Example 1
**Input (Markdown content):**

```markdown
To run the script, use the following command:  

```bash
python script.py --input file.txt --output result.json --verbose
```
```

**Output:**  
--input file.txt --output result.json --verbose

Example 2  
**Input (Markdown content):**

```markdown
Example usage:  

```sh
./analyze.sh data.csv --mode full --log-level debug
```
```

**Output:**  
data.csv --mode full --log-level debug

Example 3  
**Input (Markdown content):**  
```markdown
Run the tool with:  

```shell
tool.exe /config=config.yaml /debug
```
```

**Output:**  
/config=config.yaml /debug

    """

    PROMPT_SCRIPT_ANALYZER = "Please analyze this script and provide requirements:\n\n{script_content}"

    PROMPT_DOCKERFILE_GENERATOR = """
    Please generate a Dockerfile for a script with the following requirements:
    {requirements}
    
    The dockerfile should support the following execution command:
    {command}
    
    The script file '{script_filename}' will be in the same directory as the Dockerfile.
    Make sure to reference it correctly in the COPY and CMD instructions.
    """

    PROMPT_DOCKERFILE_ERROR = """
    The Dockerfile failed to build the image with the following error: {error}.
    Please correct the Dockerfile and try again.
    """

    PROMPT_EXAMPLE_ANALYZER = "Please analyze this example file and provide the execution arguments:\n\n{example_content}"


# Constants related to Vendor Types
ValidVendorArgument = Literal["openai", "google"]
VALID_VENDORS: Tuple[ValidVendorArgument, ...] = typing.get_args(ValidVendorArgument)


MAX_GENERATION_ATTEMPTS = 5  # Maximum number of attempts to generate a valid Dockerfile
