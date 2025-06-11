# internal library imports
import json
import os
import time
from typing import Any, Dict, Optional

# 3rd party imports
import anthropic
from anthropic import InternalServerError
from dotenv import load_dotenv
from loguru import logger
import re
import yaml

# ------------------------------------------------------------------------------
# config and params
# ------------------------------------------------------------------------------

# custom/internal imports
load_dotenv(override=True)

with open('config/model_v1.3.5.yaml', 'r') as file:
    model_config = yaml.safe_load(file)

# ------------------------------------------------------------------------------
# extraction function for use with json
# ------------------------------------------------------------------------------

def extract_with_tool(
    prompt_object: dict,
    tool: dict,
    api_key: str = os.getenv('ANTHROPIC_API_KEY'),
    model: str = model_config['anthropic_model_version'],
    max_tokens: int = 2048,
) -> Any:
    """
    Calls the Anthropic API using tools to extract structured data from prompts.

    :param prompt_object: json object contain prompt and all need prompt vars
    :param tool: Key for the tool configuration in YAML file
    :param api_key: Anthropic API key
    :param model: Claude model to use
    :param max_tokens: Maximum tokens for response
    :return: Extracted data from the tool response
    """
    # format prompt object
    formatted_prompt = json.dumps(prompt_object, indent=2)

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # log prompt to console
    log_output = f"prompt: {str(prompt_object['prompt'])[:60].replace(chr(10), ' ')}...\n"
    logger.info(log_output.strip())

    # Make API call
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": formatted_prompt}]
    )

    # log output to console
    response_text = str(response.content[0])
    log_output = f"output: {response_text[:60].replace(chr(10), ' ')}...\n"
    logger.info(log_output.strip())

    # log full prompt to file
    logger.debug(f"Full prompt: {formatted_prompt}")

    # log full output to file
    response_data = {
        "content": [{"type": content.type, "data": content.input if hasattr(content, 'input') else str(content)} for content in response.content],
        "usage": response.usage.__dict__
    }
    logger.debug(f"Full response: {json.dumps(response_data["content"][0]["data"], indent=2)}")

    # Extract structured data from tool response
    for content in response.content:
        if content.type == "tool_use" and content.name == tool["name"]:
            return content.input

    raise ValueError("No valid tool response found")

# ------------------------------------------------------------------------------
# extraction function for use without json
# ------------------------------------------------------------------------------

def complete_single_content(
    content,
    max_tokens=2048
):
    """
    Calls the Anthropic chat completion API and returns the text component of the
    API response. Includes retry logic for overloaded server errors.

    :param content: string to be passed to the API
    :param max_tokens: max tokens for allowed response
    :return: text component of the API response
    """
    client = anthropic.Anthropic()
    start_time = time.time()
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            completion = client.messages.create(
                model=model_config['anthropic_model_version'],
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": str(content)}
                ]
            )

            end_time = time.time()
            duration = end_time - start_time

            log_output = (
f"""query returned from Anthropic API
API call duration:    {duration}
input tokens:         {completion.usage.input_tokens}
output tokens:        {completion.usage.output_tokens}
"""
            )

            if model_config['verbose_prompt']:
                log_output += f"prompt:               {content.replace('\n', ' ')}\n"
            else:
                log_output += f"prompt:               {content[:60].replace('\n', ' ')}...\n"
            if model_config['verbose_output']:
                log_output += f"output:               {completion.content[0].text.replace('\n', ' ')}\n"
            else:
                log_output += f"output:               {completion.content[0].text[:60].replace('\n', ' ')}...\n"

            log_output += (
f"""API call duration:    {duration}
input tokens:         {completion.usage.input_tokens}
output tokens:        {completion.usage.output_tokens}"""
            )
            logger.info(log_output)

            return completion.content[0].text

        except InternalServerError as e:
            error_dict = e.response.json() if hasattr(e, 'response') else {}
            if error_dict.get('error', {}).get('type') == 'overloaded_error':
                if attempt < max_retries - 1:
                    logger.info(
                        f"Server overloaded. Attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.info("Max retries reached. Server still overloaded.")
            else:
                logger.info(f"An unexpected InternalServerError occurred: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

# ------------------------------------------------------------------------------
# end of single_content_completion.py
# ------------------------------------------------------------------------------
