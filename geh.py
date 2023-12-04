import os
from dotenv import load_dotenv
load_dotenv()

import requests
from requests_html import HTMLSession

import openai
openai.api_key = os.environ.get("open_ai_key")

import pygsheets
file_path = os.getcwd()
gc_client = pygsheets.authorize(client_secret=f'{file_path}/client_secret.json')

import datetime
from datetime import datetime,timedelta
import pytz
utc_now = datetime.utcnow()
nyc_timezone = pytz.timezone('America/New_York')
start_date = utc_now.astimezone(nyc_timezone) + timedelta(days=2)
end_date = start_date + timedelta(days=6)
start_date = start_date.strftime('%Y-%m-%d')
end_date = end_date.strftime('%Y-%m-%d')

event_tags = ['climate','climatechange','climate_change','sustainability','zerowaste','zero_waste','cleanup','clean_up','sustainablefashion','sustainable_fashion','compost']
event_titles = []
event_dicts = []

def summarize(event_description):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=[
        {"role": "user", "content": f'Summarize the following text in 3-4 sentences without any introductory phrases or meta-comments: {event_description}'}
    ]
    )
    return response.choices[0].message.content

def get_events(tags,titles,events):
    for tag in tags:
        try:
            print(f'#~~~~~~~~~~{tag}~~~~~~~~~~#')
            session = HTMLSession()
            event_list = session.get(f'https://www.eventbrite.com/d/ny--new-york/%23{tag}/?page=1&start_date={start_date}&end_date={end_date}').html.find('.search-main-content__events-list-item')
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
                                description = event_page.html.find('.eds-text--left')
                                # new_event_dict['description'] = description[0].text
                                summarized_description = summarize(description[0].text)
                                new_event_dict['description'] = summarized_description
                            except:
                                new_event_dict['description'] = 'See event page for event description details.'
                            new_event_dict['link'] = link
                            if new_event_dict['title'] not in titles:
                                titles.append(new_event_dict['title'])
                                events.append(new_event_dict)
                                print(new_event_dict)
                        except:
                            print(f'Something wrong with link {link}')
        except requests.exceptions.RequestException as e:
            print(e)
    return events

# exporting data to Google Sheet
def export_sheets(events,start_date,end_date):
    try:
        geh_workbook = gc_client.open('Green Events Hub - Event Log')
        new_sheet = geh_workbook.add_worksheet(f'{start_date} - {end_date}', rows=100, cols=26, src_tuple=None, src_worksheet=None, index=None)
        new_sheet.update_value('A1','Title')
        new_sheet.update_value('B1','Tag')
        new_sheet.update_value('C1','Date')
        new_sheet.update_value('D1','Description')
        new_sheet.update_value('E1','Link')
        counter = 2
        for event_dict in events:
            new_sheet.update_value(f'A{counter}',event_dict['title'])
            new_sheet.update_value(f'B{counter}',event_dict['tag'])
            new_sheet.update_value(f'C{counter}',event_dict['date'])
            new_sheet.update_value(f'D{counter}',event_dict['description'])
            new_sheet.update_value(f'E{counter}',event_dict['link'])
            counter += 1
    except Exception as e:
        print(e)
        print("Oops! There was some issue with exporting to Google Sheets! Please erase the recently created tab, wait a moment, and run the program again")


# main
upcoming_events = get_events(event_tags,event_titles,event_dicts)
export_sheets(upcoming_events,start_date,end_date)
print("All done!")
