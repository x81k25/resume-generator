import time
from src.utils.logger import log

def complete_single_content(client, content, temp=1.0):
    """
    Calls the OpenAI chat completion API and returns the text component of the
    API response.
    :param client: OpenAI client object
    :param content: string to be passed to the API
    :param temp: affects randomness of the response on a range of 0 to 2,
        with 0 being the most rigid and 2 being the most creative
    :return: text component of the API response
    """
    #print('"' + content[:20] + '..."')

    start_time = time.time()
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=temp
    )
    end_time = time.time()
    duration = end_time - start_time

    # display information about API call

    print_output = (
        "submitting query to OpenAI API\n" +
        f"API call duration:    {duration}\n" +
        f"input tokens:         {completion.usage.prompt_tokens}\n" +
        f"output tokens:        {completion.usage.completion_tokens}\n" +
        f"prompt:               {content}..." + "\n" +
        #f"prompt:               {content[:40].replace('\n', ' ')}..." + "\n" +
        f"output:               {completion.choices[0].message.content}"
        #f"output:               {completion.choices[0].message.content[:40].replace('\n', ' ')}"
    )

    log(print_output)

    # return text component of API response
    return completion.choices[0].message.content
