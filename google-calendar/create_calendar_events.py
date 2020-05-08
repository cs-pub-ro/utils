from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import sys
import csv
import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """
    Populates Calendar entries from csv file, using Google Calendar API.
    Logs the created entries in `created-events.log`.
    """
    parser = argparse.ArgumentParser(description='Populates Calendar entries from csv file, using Google Calendar API.')
    parser.add_argument('-i', '--input_file', type=str, required=True,
                        help="path to csv file with Calendar planning")
    parser.add_argument('-l', '--log_file', type=str, default='created-events.log',
                        help="path to log file")
    args = parser.parse_args()

    creds = None
    """
    The file token.pickle stores the user's access and refresh tokens, and is
    created automatically when the authorization flow completes for the first
    time.
    """
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    events = get_events_from_csv(args.input_file)
    with open(args.log_file, 'w') as log_file:
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        log_file.write("[{0}] Creating events\n".format(now))
        for event in events:
            # Call the Calendar API
            event_result = service.events().insert(calendarId='d2biu4r5gcv83ndamn6tpe0onc@group.calendar.google.com',
                                                   body=event,
                                                   sendNotifications=True).execute()
            log_file.write("Event created for: {0}. Link: {1}\n".format(event['summary'], event_result.get('htmlLink')))

def get_events_from_csv(csv_file):
    events = []
    with open(csv_file, 'r') as f:
        r = csv.reader(f)
        header = None
        for row in r:
            if header is None:
                header = row
            else:
                d = {}
                for idx in range(len(header)):
                    d[header[idx]] = row[idx]
                events.append(d)

    gapi_events = []
    for event in events:
        # Use * operator on list to expand elements so we can call format() with the
        # result of split
        # Ex. foo(*[e1, e2, e3]) -> foo(e1, e2, e3)
        start_date = '{2}-{0}-{1}'.format(*event['Start Date'].split('/'))
        start_time_hlp = event['Start Time'].split(' ')
        start_time = [int(x) for x in start_time_hlp[0].split(':')]
        if start_time_hlp[1].lower() == 'pm':
            start_time[0] += 12
        start_time = ':'.join([str(x) for x in start_time])

        end_date = '{2}-{0}-{1}'.format(*event['End Date'].split('/'))
        end_time_hlp = event['End Time'].split(' ')
        end_time = [int(x) for x in end_time_hlp[0].split(':')]
        if end_time_hlp[1].lower() == 'pm':
            end_time[0] += 12
        end_time = ':'.join([str(x) for x in end_time])

        event_json = {
            'summary': event['Subject'],
            'location': event['Location'],
            'start': {
                'dateTime': '{0}T{1}+02:00'.format(start_date, start_time),
                'timeZone': 'Europe/Bucharest'
            },
            'end': {
                'dateTime': '{0}T{1}+02:00'.format(end_date, end_time),
                'timeZone': 'Europe/Bucharest'
            },
            'attendees': [ {'email': guest} for guest in event['Guests'].split(' ') if guest != '']
        }

        gapi_events.append(event_json)

    return gapi_events

if __name__ == '__main__':
    main()
