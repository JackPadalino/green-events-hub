import os
from dotenv import load_dotenv
load_dotenv()
import requests
import openai
import json
from events import test_events_list

openai.api_key = os.environ.get("open_ai_key")

def summarize(event_dicts):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-1106",
    messages=[
        # {"role": "user", "content": f'I am sending you a Python list. Each item in the list is a string. Please summarize each item in the list to be 2 to 3 sentences in length, and then return the list still as a Python list. Please do not include anyting else in your response other than the list of strings. The only items in the list should be strings. Nothing else. Please respond in JSON Here is the list: {event_desc_list}'}
        {"role": "user", "content": f'I am sending you a Python list that contains multiple dictionaries. Each dictionary has a key/value pair for "description". Please summarize the description for each dictionary into 2 to 3 sentences, and then return the list of dictionaries back to me. Do not change the formatting of the list, do not include anything else in your response other than the list of dictionaries, and please respond in JSON. Here is the list of dictionaries: {event_dicts}'}
    ],
    )

    response = response.choices[0].message.content
    response = json.loads(response)
    return response

summarized_events = summarize(test_events_list)
print(summarized_events)
print(type(summarized_events))