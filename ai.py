import os
from dotenv import load_dotenv
load_dotenv()
import requests
import openai
import json
from event_list import event_desc_list

openai.api_key = os.environ.get("open_ai_key")

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo-16k",
  messages=[
    # {"role": "system", "content": "Give the model some context. Describe their role and their expected writing/response style"},
    {"role": "user", "content": f'I am sending you a Python list. Each item in the list is a string. Please summarize each item in the list into 4 sentences of less, and then return the list. Please do not include anyting else in your response other than the list of strings. Here is the list: {event_desc_list}'}
  ]
)
print(response.choices[0].message.content)