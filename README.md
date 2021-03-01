# GmailFilters
Some tools to manage large numbers of Gmail filters.

## External Docs and Resources

These tools use the Gmail API. To run these scripts you will need to enable the API on your account following the [instructions here](https://developers.google.com/gmail/api/quickstart/python) for creating an API Key and Credentials.

The process of [creating an API account with the Google developer console](https://console.developers.google.com/apis) will require creating and copying locally the credentials as `credentials.json` in the same path as the tools. I went with creating an "OAuth 2.0 Client IDs" entry and clicking the `Download JSON` link.

The API documentation for [filters is here](https://developers.google.com/gmail/api/guides/filter_settings). I also found [this document](https://developers.google.com/gmail/api/auth/web-server) helpful when working through the process of getting the authentication working.

The first time in a while that any of the tools are run you may be directed to log in and accept the features of the tool. _I have found problems with this workflow if the browser used for accepting the features is not the Chrome browser._

## FindOldFilters.py
This is for pulling down the full list of filters on a Gmail account and storing them into a local file. Further processing of the list of filters divides the list into "active" and "old" filters: a search is run based on the rules of the filter and if e-mails are found that were received less than a year ago the filter is considered "active".

## FixFiltersToNotRemoveInbox.py
I had a lot of filters that assign a label and alos remove the Inbox label from the e-mail (archiving it). I later decided that workflow wasn't very effective for me and wanted to keep the e-mails in the Inbox until I had a chance to acknowledge them. There isn't a way in Gmail to apply a change in rules across a batch of filters, so this tool was useful to remove the archiving action on a large number of filters.

Filters are taken from the "active" list prepared by `FindOldFilters` and operated on ~10 at a time by default, tracking which ones are relevant (have the `removeLabelIds` action) and which have already been processed. The operation is destructive: the old filter is `delete`-d and a new one without the Inbox removal action is `create`-d, and the `create` process can be rather slow so batching in groups of ~10 helped in troubleshooting if something looked wrong. (Final execution had no issues.)

## PruneOldFilters.py
This tool calls for a `delete` of the "old" filters discovered by `FindOldFilters`.
