from __future__ import print_function
import json
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# https://developers.google.com/gmail/api/guides/filter_settings

# https://developers.google.com/gmail/api/quickstart/python

# https://developers.google.com/gmail/api/auth/web-server
# Path to client_secrets.json which should contain a JSON document such as:
#   {
#     "web": {
#       "client_id": "[[YOUR_CLIENT_ID]]",
#       "client_secret": "[[YOUR_CLIENT_SECRET]]",
#       "redirect_uris": [],
#       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#       "token_uri": "https://accounts.google.com/o/oauth2/token"
#     }
#   }

# If modifying these scopes, delete the file token.pickle.
# https://developers.google.com/gmail/api/reference/rest/v1/users.settings.filters/list
SCOPES = [
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None

    # Remove/comment-out these lines to actually process this script
    print("This work is done, unless it's been a while")
    return

    print("Setting things up...")

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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

    service = build('gmail', 'v1', credentials=creds)

    # example_filter_id = "" # put in filter ID to test these lines
    # # results = service.users().settings().filters().get(userId='me', id=example_filter_id).execute()
    # # results = service.users().settings().filters().delete(userId='me', id=example_filter_id).execute()

    print("Getting list of GMail filters...")
    filters = {}
    filters_topurge = []
    filters_previously_purged = []

    old_filters_base_filename = 'filters-20210227-old'
    old_filters_filename = old_filters_base_filename + '.json'
    purged_filters_filename = old_filters_base_filename + '-purged.json'

    with open(old_filters_filename, 'r') as file_object:
       filters = json.loads(file_object.read())
    print("Total old filters: " + str(len(filters)))

    with open(purged_filters_filename, 'r') as file_object:
        filters_previously_purged = json.loads(file_object.read())

    if not filters:
        print('Exiting: no old filters to process.')
    else:
        print("Finding old filters to purge...")
        for f in filters:
            if f not in filters_previously_purged:
                filters_topurge.append(f)

    print('Filters found to be purged: ' + str(len(filters_topurge)))

    capped_filters_topurge = filters_topurge[:100]
    print(f"Purging ({str(len(capped_filters_topurge))}) filters...")

    filters_purged = filters_previously_purged
    count_filters_purged = 0
    for f in capped_filters_topurge:
        count_filters_purged += 1
        print(f"...{count_filters_purged}")
        filters_purged.append(f)
        purge_filter(service, f)

    with open(purged_filters_filename, "w") as processed_filters_file:
        processed_filters_file.write(json.dumps(filters_purged))


def purge_filter(service, filter_topurge):
    processing_filter_topurge_id = filter_topurge['id']
    print(f"\tdelete: {processing_filter_topurge_id}")
    results = service.users().settings().filters().delete(userId='me', id=processing_filter_topurge_id).execute()
    # print(results)


if __name__ == '__main__':
    main()