# fetch_data.py
# Authored by Arthur Delarue on 5/28/2015
# Adapted from https://cloud.google.com/bigquery/bigquery-api-quickstart

import httplib2
import pprint
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools

queryString = 'SELECT pickup_datetime, dropoff_datetime FROM [833682135931:nyctaxi.trip_data] LIMIT 10;'

def fetch_data(queryStr=queryString):

  # Enter your Google Developer Project number
  PROJECT_NUMBER = '921050816021'

  # Load identification information from JSON file
  FLOW = flow_from_clientsecrets('client_secret.json',
                                 scope='https://www.googleapis.com/auth/bigquery')
  storage = Storage('bigquery_credentials.dat')
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    # Run oauth2 flow with default arguments.
    credentials = tools.run_flow(FLOW, storage, tools.argparser.parse_args([]))

  http = httplib2.Http()
  http = credentials.authorize(http)

  # Build BigQuery client
  bigquery_service = build('bigquery', 'v2', http=http)

  # Create a query statement and query request object
  query_data = {'query':queryString}
  query_request = bigquery_service.jobs()

  # Make a call to the BigQuery API
  query_response = query_request.query(projectId=PROJECT_NUMBER,
                                   body=query_data).execute()
  # Output results
  f = open("output.txt", "w")
  f.write('Query Results:\n')
  for row in query_response['rows']:
      result_row = []
      for field in row['f']:
          result_row.append(field['v'])
      f.write(('\t').join(result_row))
      f.write('\n')
  f.close()
  return None

#fetch_data()

