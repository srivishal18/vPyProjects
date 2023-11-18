from datetime import datetime
import datetime
import pytz
import re

from googleapiclient.discovery import build

import os
import openai
import creds

openai.api_key = ""
os.environ["OPENAI_API_KEY"] = ""
cred = creds.getCreds()

"""

CHANGE WHATEVER TIMEZONE INTO UTC AND THEN WORK ON THE FUNCTIONS

"""
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("Time right now: ", now)

def create(summary = "", date = "", time = "", description = ""):
    print(summary, date, time, description)
    
    
    
    service = build('calendar', 'v3', credentials=creds.getCreds())
   
    dT = openai.Completion.create(engine = "text-davinci-002", prompt=f"Give the following date in YYYY-MM-DD form {date}, given today is {now}", max_tokens=100, temperature=0).choices[0].text.strip()
    tT = openai.Completion.create(engine = "text-davinci-002", prompt=f"Give the following time in HH:MM:SS form {time}", max_tokens=100, temperature=0).choices[0].text.strip()
    d = list(map(int, re.search("\d{4}-\d{2}-\d{2}", dT).group().split('-')))
    t = list(map(int, re.search("\d{2}:\d{2}:\d{2}", tT).group().split(':')))
    
    dateT = datetime.datetime(d[0], d[1], d[2], t[0], t[1], t[2]).isoformat()
    event = {
        'summary': summary,
        'location': 'Online',
        'description': description,
        'start': {
            'dateTime': f'{dateT}-05:00', # set start date and time in ISO format
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': (datetime.datetime.strptime(f'{dateT}-05:00', '%Y-%m-%dT%H:%M:%S%z') + datetime.timedelta(hours=1)).isoformat(), # set end date and time in ISO format
            'timeZone': 'America/New_York',
        },
        'reminders': {
            'useDefault': True, # set to True to use the default reminders
        },
    }

    print(event)
    event = service.events().insert(calendarId='primary', body=event).execute()

    print(f'Event created: {event.get("htmlLink")}')
    eventres = event.get("htmlLink")

    return eventres


def change(summary = "", date = "", time = ""):
    service = build('calendar', 'v3', credentials=creds.getCreds())
    print(date, time)

# Specify the event name you want to update

    # List events based on the event name
    events = service.events().list(calendarId='primary', q=summary).execute()
    matched_events = events.get('items', [])
    
    dT = openai.Completion.create(engine = "text-davinci-002", prompt=f"Give the following date in YYYY-MM-DD form {date}, given today is {now}", max_tokens=100, temperature=0).choices[0].text.strip()
    tT = openai.Completion.create(engine = "text-davinci-002", prompt=f"Give the following time in HH:MM:SS form {time}", max_tokens=100, temperature=0).choices[0].text.strip()
    d = list(map(int, re.search("\d{4}-\d{2}-\d{2}", dT).group().split('-')))
    t = list(map(int, re.search("\d{2}:\d{2}:\d{2}", tT).group().split(':')))
    
    dateT = datetime.datetime(d[0], d[1], d[2], t[0], t[1], t[2]).isoformat()
    if len(matched_events) > 0:
        # Choose the first matched event
        event = matched_events[0]

        event['start']['dateTime'] = f'{dateT}-05:00'
        event['end']['dateTime'] = (datetime.datetime.strptime(f'{dateT}-05:00', '%Y-%m-%dT%H:%M:%S%z') + datetime.timedelta(hours=1)).isoformat(), # set end date and time in ISO format

        # Make the API request to update the event
        updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()

        return ('Event updated: {}'.format(updated_event['summary']))
    else:
        return ('No event found with the specified name.')


def utc_iso(chicago_time_str):
    '''
    
    the format for input time should be like below. It's the same format as now at the beginning of the code.
    input_time = "2023-08-12 19:13:07" "2023-08-17 7:00:00"
    
    '''
    # Specify the source and target time zones
    chicago_timezone = pytz.timezone("America/Chicago")
    utc_timezone = pytz.timezone("UTC")

    # Convert the input Chicago time to a datetime object
    chicago_time = datetime.datetime.strptime(chicago_time_str, "%Y-%m-%d %H:%M:%S")

    # Convert Chicago time to UTC time
    utc_time = chicago_timezone.localize(chicago_time).astimezone(utc_timezone)

    # Format the UTC time as ISO 8601 string
    utc_iso = utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    return utc_iso # Returns utc time from chicago's timezone time.


def view_events():
    service = build('calendar', 'v3', credentials=creds.getCreds())
    
    now = datetime.datetime.utcnow()
    
    time_max = now.replace(hour=23, minute=59, second=59, microsecond=0)
    
    time_min_str = now.isoformat() + "Z"
    time_max_str = time_max.isoformat() + "Z"
    

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min_str,
        timeMax=time_max_str,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime').execute()

    events = events_result.get('items', [])
    if not events:
        print('No events found for today.')
    else:
        print('Events for today:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} - {event['summary']}")


def get_event_id(event_name): # Only if the Event name is accurate
    
    service = build('calendar', 'v3', credentials=creds.getCreds())
    now = datetime.datetime.utcnow()
    
    # Set timeMin to the current time (UTC)
    time_min_str = now.isoformat() + "Z"

    # Searches for events with the name
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min_str,
        q=event_name, 
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    
    for event in events:
        # Only if the Event name is accurate
        if event.get('summary') == event_name:
            # print(event.get("summary"))
            return event['id']

    # If no matching event is found
    return None


def modify_event(event_name, start_time, end_time):

    event_id = get_event_id(event_name)
    service = build('calendar', 'v3', credentials=creds.getCreds())

    # Get the event
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    # Modify start and end times
    event['start']['dateTime'] = start_time
    event['end']['dateTime'] = end_time

    # Update the event
    updated_event = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event
    ).execute()

    print("Event updated")


# event_name = "Movie"
# new_start_time = utc_iso('2023-08-16 12:00:00') # Format: YYYY-MM-DD HH:MM:SS
# new_end_time = utc_iso('2023-08-16 13:30:00') # Format: YYYY-MM-DD HH:MM:SS


# # make a random event and also a title and then change accordingly

# modify_event(event_name, new_start_time, new_end_time)

def delete_event_by_name(event_name):
    
    service = build('calendar', 'v3', credentials=creds.getCreds())
    
    # List events based on the event name
    events = service.events().list(calendarId='primary', q=event_name).execute()
    matched_events = events.get('items', [])
    
    if matched_events:
        # Delete each matched event
        for event in matched_events:
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
        
        return f"Deleted {len(matched_events)} event(s) with the name '{event_name}'."
    else:
        return f"No event found with the name '{event_name}'."

"""For DELETE BY NAME"""
# Example usage
# event_name_to_delete = "A"
# result = delete_event_by_name(event_name=event_name_to_delete)
# print(result)
# view_events()
"""For DELETE BY NAME"""

def delete_event(start_time):

    service = build('calendar', 'v3', credentials=creds.getCreds())

    target_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")

    
    time_min_obj = target_datetime 
    time_max_obj = target_datetime + datetime.timedelta(minutes=10)

    time_min_iso = time_min_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    time_max_iso = time_max_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(time_min_iso)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min_iso,
        timeMax=time_max_iso
    ).execute()

    events = events_result.get('items', [])

    for event in events:
        event_id = event['id']
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print('Event deleted:', event['summary'])

'''FOR DELETE EVENT'''
# start_time = "2023-08-17 8:00:00"
# delete_event(utc_iso(start_time))
# # # view_events()
'''FOR DELETE EVENT'''

def update_event_location(event_id, new_location):
    service = build('calendar', 'v3', credentials=creds.getCreds())

    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['location'] = new_location

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print('Event updated:', updated_event.get('htmlLink'))

""" UPDATE """
# event_id_to_update = get_event_id('Movie')
# new_event_location = 'AMC'
# update_event_location(event_id_to_update, new_event_location)
""" UPDATE """

def update_event_guests(event_id, new_guest_emails):
    service = build('calendar', 'v3', credentials=creds.getCreds())

    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['attendees'] = [{'email': email} for email in new_guest_emails]

    updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    print('Event updated:', updated_event.get('htmlLink'))

"""ADD GUESTS"""    
# event_id_to_update = get_event_id('Movie')
# new_guest_emails = ['vishalramya10@gmail.com']  # Add new guest emails here
# update_event_guests(event_id_to_update, new_guest_emails)
"""ADD GUESTS"""

def know_event(event_name):

    service = build('calendar', 'v3', credentials=creds.getCreds())

    events_result = service.events().list(calendarId='primary', q=event_name).execute()
    events = events_result.get('items', [])

    if not events:
        return "Event not found."

    event = events[0]
    start_time_str = event['start'].get('dateTime', event['start'].get('date'))

    start_time = datetime.datetime.fromisoformat(start_time_str)
    human_readable_time = start_time.strftime('%B %d, %Y %I:%M %p')  # Customize the format as needed

    return f"The event '{event_name}' is scheduled for {human_readable_time}."

"""WHEN MY EVENT"""
# event_name_to_search = 'Movie'  
# ev_time = know_event(event_name_to_search)
# print(ev_time)
""" WHEN MY EVENT """