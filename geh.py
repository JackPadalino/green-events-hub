import os
import requests
from requests_html import HTMLSession
from dotenv import load_dotenv
load_dotenv()
import openai
import pygsheets

openai.api_key = os.environ.get("open_ai_key")
gc_client = pygsheets.authorize(client_secret='/Users/snerd/Desktop/projects/pythonprojects/eventbrite-scraper/client_secret.json')
tags = ['climate','climatechange','climate_change','sustainability','zerowaste','zero_waste','cleanup','clean_up','sustainablefashion','sustainable_fashion']
event_dict_list = []
event_titles_list = []

def summarize(event_description):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        # {"role": "system", "content": "Give the model some context. Describe their role and their expected writing/response style"},
        {"role": "user", "content": f'I am going to give you a short text to summarize. Please summarize the text into 4 sentences or less. Do not include anything else in your response other than the summarized text. Here is the text I want you to summarize: {event_description}'}
    ]
    )
    return response.choices[0].message.content

for tag in tags:
    print(f'#~~~~~~~~~~{tag}~~~~~~~~~~#')
    print('\n')
    try:
        session = HTMLSession()
        event_list = session.get(f'https://www.eventbrite.com/d/ny--new-york/events--next-week/%23{tag}/?page=1').html.find('.search-main-content__events-list-item')
        for event in event_list:
            new_event_dict = {}
            new_event_dict['tag'] = tag
            if not 'Promoted' in event.text.split():
                for link in event.links:
                    try:  
                        event_page = session.get(link)
                        try:
                            title = event_page.html.find('.event-title')
                            new_event_dict['title'] = title[0].text
                        except:
                            new_event_dict['title'] = 'See event page for title details.'
                        try:
                            date = event_page.html.find('.date-info__full-datetime')
                            new_event_dict['date'] = date[0].text
                        except:
                            new_event_dict['date'] = 'See event page for event date and time details.'
                        try:
                            # using Open AI API to summarize descriptions
                            description = event_page.html.find('.eds-text--left')
                            summarized_description = summarize(description[0].text)
                            new_event_dict['description'] = summarized_description
                            # new_event_dict['description'] = description[0].text
                            # event_descriptions_list.append(description[0].text)
                        except:
                            new_event_dict['description'] = 'See event page for event description details.'
                        new_event_dict['link'] = link
                        if new_event_dict['title'] not in event_titles_list:
                            event_titles_list.append(new_event_dict['title'])
                            event_dict_list.append(new_event_dict)
                            print(new_event_dict)
                            print('\n')
                    except:
                        print(f'Something wrong with link {link}')

    except requests.exceptions.RequestException as e:
        print(e)

print(event_dict_list)

# exporting data to Google Sheet
geh_workbook = gc_client.open('Green Events Hub')
new_sheet = geh_workbook.add_worksheet('Events next week', rows=100, cols=26, src_tuple=None, src_worksheet=None, index=None)
new_sheet.update_value('A1','Title')
new_sheet.update_value('B1','Tag')
new_sheet.update_value('C1','Date')
new_sheet.update_value('D1','Description')
new_sheet.update_value('E1','Link')
counter = 2
for event_dict in event_dict_list:
    new_sheet.update_value(f'A{counter}',event_dict['title'])
    new_sheet.update_value(f'B{counter}',event_dict['tag'])
    new_sheet.update_value(f'C{counter}',event_dict['date'])
    new_sheet.update_value(f'D{counter}',event_dict['description'])
    new_sheet.update_value(f'E{counter}',event_dict['link'])
    counter += 1
