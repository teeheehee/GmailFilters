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

    print("Getting list of GMail filters...")
    filters = {}

    with open('filters-20210227.json', 'r') as file_object:
       filters = json.loads(file_object.read())

    print(f"Total stored filters: {str(len(filters))}")

    # results = service.users().settings().filters().list(userId='me').execute()
    # filters = results['filter']

    # with open('filters-20210227.json', 'w') as file_object:
    #    file_object.write(json.dumps(filters))

    # print(f"Total GMail filters: {str(len(filters))}")
    # return

    print("Finding old filters...")

    old_filters = []
    active_filters = []
    report_progress_every_n = 5
    count_of_filters_checked = 0
    for f in filters:
        count_of_filters_checked += 1
        if count_of_filters_checked % report_progress_every_n == 0:
            print(f"\t({count_of_filters_checked}): old({str(len(old_filters))}), active({str(len(active_filters))})")

        if has_filter_been_used_recently(service, f):
            active_filters.append(f)
        else:
            old_filters.append(f)

    old_filters_filename = 'filters-20210227-old.json'
    print(f"Old filters saved to: {old_filters_filename}")
    with open(old_filters_filename, 'w') as file_old_filters:
        file_old_filters.write(json.dumps(old_filters))

    active_filters_filename = 'filters-20210227-active.json'
    print(f"Active filters saved to: {active_filters_filename}")
    with open(active_filters_filename, 'w') as file_active_filters:
        file_active_filters.write(json.dumps(active_filters))


def has_filter_been_used_recently(service, filter):
    criteria_query = create_query_string_from_filter(filter, 1)
    results = service.users().messages().list(userId='me', maxResults=10, includeSpamTrash=1, q=criteria_query).execute()
    # if not results['resultSizeEstimate'] > 0:
    #     print("Filter with no results: " + criteria_query)
    return results['resultSizeEstimate'] > 0

def create_query_string_from_filter(filter, add_one_year_limit):
    criteria = []
    if add_one_year_limit:
        criteria.append("newer_than:1y")
    for q in filter['criteria']:
        if (q == "query"):
            criteria.append(filter['criteria'][q])
        else:
            criteria.append(f"{q}:{filter['criteria'][q]}")
    criteria_clause = " ".join(criteria)
    # print("Filter: " + criteria_clause)
    return criteria_clause

if __name__ == '__main__':
    main()