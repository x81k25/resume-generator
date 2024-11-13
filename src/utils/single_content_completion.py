import anthropic
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
    :param max_tokens: max tokens for allowed response
    :param content: string to be passed to the API
    :param temp: affects randomness of the response on a range of 0 to 2,
        with 0 being the most rigid and 2 being the most creative
    :return: text component of the API response
    """
    client = client = anthropic.Anthropic()

    start_time = time.time()
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

    #completion.content[0].type

    print_output = (
        "query returned from Antrhopic API\n" +
        f"API call duration:    {duration}\n" +
        f"input tokens:         {completion.usage.input_tokens}\n" +
        f"output tokens:        {completion.usage.output_tokens}\n" +
        #f"prompt:               {content}..." + "\n" +
        f"prompt:               {content[:60].replace('\n', ' ')}..." + "\n" +
        f"output:               {completion.content[0].text}"
        #f"output:               {completion.choices[0].message.content[:40].replace('\n', ' ')}"
    )

    log(print_output)

    # return text component of API response
    return completion.content[0].text
