from __future__ import print_function
import copy
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
    # example_from_address = "" # put an example e-mail address in for a filter
    # example_label_id = "Label_1" # put a different label id hook here
    # # results = service.users().settings().filters().get(userId='me', id=example_filter_id).execute()
    # filter_to_replace = {'id': example_filter_id, 'criteria': {'from': example_from_address}, 'action': {'addLabelIds': [example_label_id], 'removeLabelIds': None}}
    # filter_replaced = {'criteria': {'from': example_from_address}, 'action': {'addLabelIds': [example_label_id], 'removeLabelIds': None}}
    # # results = service.users().settings().filters().delete(userId='me', id=example_filter_id).execute()
    # # results = service.users().settings().filters().create(userId='me', body=filter_replaced).execute()

    print("Getting list of GMail filters...")
    filters = {}
    filters_tofix = []
    filters_previously_fixed = []

    active_filters_base_filename = 'filters-20210227-active'
    active_filters_filename = active_filters_base_filename + '.json'
    processed_active_filters_filename = active_filters_base_filename + '-processedForRemoveFromInbox.json'

    with open(active_filters_filename, 'r') as file_object:
       filters = json.loads(file_object.read())
    # results = service.users().settings().filters().list(userId='me').execute()
    # filters = results['filter']
    print("Total active filters: " + str(len(filters)))

    with open(processed_active_filters_filename, 'r') as file_object:
        filters_previously_fixed = json.loads(file_object.read())

    if not filters:
        print('Exiting: no active filters to process.')
    else:
        print("Finding filters with 'removeLabelIds'...")
        for f in filters:
            if f not in filters_previously_fixed and 'removeLabelIds' in f['action'] and 'INBOX' in f['action']['removeLabelIds']:
                filters_tofix.append(f)

    print('Filters found to be fixed: ' + str(len(filters_tofix)))

    first_ten_filters_tofix = filters_tofix[:10]
    print(f"Fixing ({str(len(first_ten_filters_tofix))}) filters...")

    filters_fixed = filters_previously_fixed
    count_filters_fixed = 0
    for f in first_ten_filters_tofix:
        count_filters_fixed += 1
        print(f"...{count_filters_fixed}")
        filters_fixed.append(f)
        replace_removeLabelIds_filter(service, f)

    with open(processed_active_filters_filename, "w") as processed_filters_file:
        processed_filters_file.write(json.dumps(filters_fixed))


def replace_removeLabelIds_filter(service, filter_tofix):
    processing_filter_tofix = copy.deepcopy(filter_tofix)
    removeLabelIds = processing_filter_tofix['action']['removeLabelIds'].remove('INBOX')
    processing_filter_tofix['action']['removeLabelIds'] = removeLabelIds
    processing_filter_tofix_id = processing_filter_tofix['id']
    processing_filter_tofix.pop('id')

    print(f"\tdelete: {processing_filter_tofix_id}")
    results = service.users().settings().filters().delete(userId='me', id=processing_filter_tofix_id).execute()
    # print(results)

    print("\tcreate")
    results = service.users().settings().filters().create(userId='me', body=processing_filter_tofix).execute()
    # print(results)



if __name__ == '__main__':
    main()