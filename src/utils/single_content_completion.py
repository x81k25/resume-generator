import anthropic
from anthropic import InternalServerError
from dotenv import load_dotenv
import time
import yaml
from src.utils.logger import log

load_dotenv()

with open('config/model_v1.25.yaml', 'r') as file:
    model_config = yaml.safe_load(file)

def complete_single_content(
    content,
    max_tokens=1024
):
    """
    Calls the OpenAI chat completion API and returns the text component of the
    API response.
    :param content: string to be passed to the API
    :param max_tokens: max tokens for allowed response
    :return: text component of the API response
    """
    client = anthropic.Anthropic()

    start_time = time.time()

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
    except InternalServerError as e:
        if e.error.get('type') == 'overloaded_error':
            # Custom response for 'Overloaded' error
            print("The server is currently overloaded. Please try again later.")
            return None
        else:
            # Log or handle other types of InternalServerError
            print(f"An unexpected InternalServerError occurred: {e}")
            return None
    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"An unexpected error occurred: {e}")
        return None

    end_time = time.time()
    duration = end_time - start_time

    #completion.content[0].type

    print_output = (
        "query returned from Antrhopic API\n" +
        f"API call duration:    {duration}\n" +
        f"input tokens:         {completion.usage.input_tokens}\n" +
        f"output tokens:        {completion.usage.output_tokens}\n" +
        #f"prompt:               {content}..." + "\n" +
        f"prompt:               {content[:60].replace('\n', ' ')}..." + "\n" +
        f"output:               {completion.content[0].text}"
        #f"output:               {completion.message.content[:40].replace('\n', ' ')}"
    )

    log(print_output)

    # return text component of API response
    return completion.content[0].text
