import os
import subprocess
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template


def execute_command(command):
    """
    Execute a shell command and return its output, return code, and error.

    Args:
        command (str): The command to execute.

    Returns:
        tuple: A tuple containing (stdout, return code, stderr).
    """
    try:
        # Run the command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        retcode = process.returncode

        # Decode the output and error
        stdout_decoded = stdout.decode('utf-8')
        stderr_decoded = stderr.decode('utf-8')

        return stdout_decoded, retcode, stderr_decoded
    except Exception as e:
        return None, 1, str(e)


# Optional: Write the rendered YAML to a file
def save_yaml_to_file(yaml_content, output_file="/tmp/serving.yaml"):
    """
    Saves YAML content to a file, creating the directory if it doesn't exist.

    :param yaml_content: Python dictionary representing the YAML content
    :param output_file: Path where YAML file will be saved
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as file:
        yaml.dump(yaml_content, file)
    return output_file


import os
from jinja2 import Template


def render_jinja2_template_to_yaml(template_path, context):
    """
    Renders a Jinja2 template with the given context and saves the result as a YAML file.

    Args:
        template_path (str): Full path to the Jinja2 template file.
        context (dict): Dictionary containing context variables to be used in the template.

    Returns:
        str: YAML content of the rendered template.
    """

    # Read template file content
    with open(template_path, 'r') as file:
        template_content = file.read()

    # Initialize Jinja2 environment using the content directly
    template = Template(template_content)

    # Render the template with the provided context
    yaml_content = template.render(context)

    # Create the output directory as 'serving_runtime_updated' in the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(template_path)))  # Navigate to the base directory
    output_dir = os.path.join(base_dir, 'odhlibs', 'serving_runtime_updated')
    os.makedirs(output_dir, exist_ok=True)

    # Define the output file path in the new directory
    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(template_path))[0]}.yaml")

    # Save the rendered content as a YAML file
    with open(output_file, 'w') as f:
        f.write(yaml_content)

    return output_file


def get_jinja_file_name(runtime_type):
    jinja_file_mapping = {
        "caikit_standalone": "caikit-standalone-serving-template.jinja2",
        "caikit_tgis": "caikit-tgis-serving-template.jinja2",
        "kserve_ovms": "kserve-ovms.jinja2",
        "tgis-grpc": "tgis-grpc-serving-template.jinja2",
        "vllm-runtime": "vllm-runtime-template.jinja2"
    }
    return jinja_file_mapping.get(runtime_type, None)


def get_elements_with_prefix(elements, prefix):
    # Filter the list of elements to match the prefix
    matching_elements = [element for element in elements if element.startswith(prefix)]

    return matching_elements