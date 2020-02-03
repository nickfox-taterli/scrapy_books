import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
import time
import socket

socket.setdefaulttimeout(1800)

# If modifying these scopes, delete the file token.google.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

creds = None
# The file token.google stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.google'):
    with open('token.google', 'rb') as token:
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
    with open('token.google', 'wb') as token:
        pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)

page_token = None
fn = '/tmp/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.csv'
while True:
    param = {'q':"'{}' in parents".format('1W14BJa9PoqPP1K4C-WhOhu9VShKMsrdF'), 'pageSize':10, 'fields':'*'}
    if page_token:
        param['pageToken'] = page_token
    items = service.files().list(**param).execute()
    for item in items['files']:
        if 'size' in item:
            if int(item['size']) < 1073741824:
                request = service.files().get_media(fileId=item['id'])
                fh = io.FileIO(fn, mode='ab')
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                service.files().delete(fileId=item['id']).execute()
    page_token = items.get('nextPageToken')
    if not page_token:
        break

file_metadata = {'name': os.path.basename(fn),
                'mimeType': 'text/csv','parents': ['1W14BJa9PoqPP1K4C-WhOhu9VShKMsrdF']}
media = MediaFileUpload(fn,
                        mimetype='text/csv')
file = service.files().create(body=file_metadata,
                            media_body=media,
                            fields='id').execute()
