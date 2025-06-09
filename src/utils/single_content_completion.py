# internal library imports
import logging
import time

# 3rd party imports
import anthropic
from anthropic import InternalServerError
from dotenv import load_dotenv
import yaml

# custom/internal imports







from src.utils.logger import log

load_dotenv()

with open('config/model_v1.3.4.yaml', 'r') as file:
    model_config = yaml.safe_load(file)






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

            print_output = (
f"""query returned from Anthropic API
API call duration:    {duration}
input tokens:         {completion.usage.input_tokens}
output tokens:        {completion.usage.output_tokens}
"""
            )

            if model_config['verbose_prompt']:
                print_output += f"prompt:               {content.replace('\n', ' ')}\n"
            else:
                print_output += f"prompt:               {content[:60].replace('\n', ' ')}...\n"
            if model_config['verbose_output']:
                print_output += f"output:               {completion.content[0].text.replace('\n', ' ')}\n"
            else:
                print_output += f"output:               {completion.content[0].text[:60].replace('\n', ' ')}...\n"

            print_output += (
f"""API call duration:    {duration}
input tokens:         {completion.usage.input_tokens}
output tokens:        {completion.usage.output_tokens}"""
            )
            log(print_output)

            return completion.content[0].text

        except InternalServerError as e:
            error_dict = e.response.json() if hasattr(e, 'response') else {}
            if error_dict.get('error', {}).get('type') == 'overloaded_error':
                if attempt < max_retries - 1:
                    print(
                        f"Server overloaded. Attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("Max retries reached. Server still overloaded.")
            else:
                print(f"An unexpected InternalServerError occurred: {e}")
            return None

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None