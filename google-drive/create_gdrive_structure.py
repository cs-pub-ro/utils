# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START drive_quickstart]
from __future__ import print_function
import pickle
import os.path
import io
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient import errors


# If modifying these scopes, delete the file token.pickle.
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SCOPES = ['https://www.googleapis.com/auth/drive']


def get(service, folder_id, name):
    results = service.files().list(q="'{}' in parents and trashed=false and name='{}'".format(folder_id, name),
        pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
    return results.get('files', [])


def ls(service, folder_id):
    # Call the Drive v3 API.
    # Use the search file fields as query (q) to filter results:
    # https://developers.google.com/drive/api/v3/search-files
    results = service.files().list(q="'{}' in parents and trashed=false".format(folder_id),
        pageSize=100, fields="nextPageToken, files(id, name, mimeType)").execute()
    return results.get('files', [])


def ls_print(service, folder_id):
    items = ls(service, folder_id)
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1}) ({2})'.format(item['name'], item['id'], item['mimeType']))


def cp(service, src_file_id, dest_folder_id, dest_file_name):
    dest_metadata = {
            'name': dest_file_name,
            'parents': [dest_folder_id]
            }
    return service.files().copy(fileId=src_file_id, body=dest_metadata).execute()


def ln(service, src_file_id, dest_folder_id):
    return service.files().update(fileId=src_file_id, addParents=dest_folder_id, fields='id, parents').execute()


def mv(service, src_file_id, dest_folder_id):
    # Retrieve the existing parents to remove.
    f = service.files().get(fileId=src_file_id, fields='parents').execute()
    previous_parents = ",".join(f.get('parents'))
    # Move file to the destination folder.
    return service.files().update(fileId=src_file_id, addParents=dest_folder_id, removeParents=previous_parents, fields='id, parents').execute()


def mkdir(service, dest_folder_id, dest_name):
    dest_metadata = {
            'name': dest_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [dest_folder_id]
            }
    return service.files().create(body=dest_metadata).execute()


def upload(service, dest_folder_id, local_file_path):
    # Insert a file. Files are comprised of contents and metadata.
    # MediaFileUpload abstracts uploading file contents from a file on disk.
    media = googleapiclient.http.MediaFileUpload(
            local_file_path,
            resumable=True
            )
    # The body contains the metadata for the file.
    file_metadata = {
            'name': os.path.basename(local_file_path),
            'parents': [dest_folder_id]
            }
    return service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def _download_from_request(request):
    fh = io.BytesIO()
    downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {:d}%%.".format(int(status.progress() * 100)))


def download(service, file_id):
    request = service.files().get_media(fileId=file_id)
    _download_from_request(request)


def download_doc(service, file_id):
    request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
    _download_from_request(request)


def init_service(credentials_filename, token_filename):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_filename):
        with open(token_filename, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_filename, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_filename, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)


course_folders = {
        'USO': '0B4hNERc1xXxGbmt1SmVYMGpEU00',
        'IOCLA': '0B3h5Op_iFi3jfkFYeXE1MFZwZlpTSTFHanJpWi0wYTNpYXRQcllVak81OVotZG4xVU9xYzg',
        'RL': '0B3h5Op_iFi3jZjNjNzgwOTEtOTFiZC00Y2NhLWE4NjEtZjA1ODA2MzY2ZjIy',
        'SO': '0B3h5Op_iFi3jZTY4ZjNhMGYtMDhiOS00NTc2LWIxN2ItMzg0YzExNGUyNjk1',
        'MPS': '0B3h5Op_iFi3jYWQyZWRiMDctNWNiZi00YzRmLWI2YmYtZmNlMzAxY2M0MDYz',
        'SO2': '0B3h5Op_iFi3jOTRkYTZlNDktNDdjNS00ODY5LWE2Y2QtYjUxMjgzZTM4YzA4',
        'GSR': '0B3h5Op_iFi3jWXpBUFcxOHRLVWs',
        'CNS': '0B3h5Op_iFi3jYjZ0WUJtWlBpdjA',
        'SIS': '0B3h5Op_iFi3jZGZwV1lkaUJQQ0k',
        'OSP': '0B3h5Op_iFi3jOTE5NzA5ZTQtNjljZC00MjNiLWEyYTQtYTY4NGRiMDIxZjEx',
        }



def usage():
    print("Usage:")
    print("  python {} <course> <academic_year>\n".format(sys.argv[0]))
    print("Sample:")
    print("  python {} SO2 2019-2020\n".format(sys.argv[0]))


def main():
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    course = sys.argv[1]
    year = sys.argv[2]
    course_folder_id = course_folders[course]
    service = init_service('credentials.json', 'token.pickle')
    item = mkdir(service, course_folder_id, '{} {}'.format(course, year))
    year_folder_id = item['id']

    # Copy template documents and link common documents in new course folder.
    items = ls(service, course_folder_id)
    for item in items:
        if item['mimeType'] != 'application/vnd.google-apps.folder':
            if item['name'].startswith('{} - '.format(course)):
                if item['name'].startswith('{} - Template -'.format(course)):
                    new_name = item['name'].replace('- Template', year)
                    cp(service, item['id'], year_folder_id, new_name)
                else:
                    ln(service, item['id'], year_folder_id)

    # Link common documents.
    #items = get(service, course_folder_id, 'Feedback')
    #if items:
    #    ln(service, items[0]['id'], year_folder_id)
    #items = get(service, course_folder_id, 'Suport')
    #if items:
    #    ln(service, items[0]['id'], year_folder_id)

    ## Create folders.
    #if course == "USO" or course == "IOCLA" or course == "SO":
    #    mkdir(service, year_folder_id, "Curs")
    #    mkdir(service, year_folder_id, "Examen")
    #    mkdir(service, year_folder_id, "Laborator")
    #    mkdir(service, year_folder_id, "Teme")
    #    mkdir(service, year_folder_id, "Lucrari de curs")
    #    mkdir(service, year_folder_id, "Studenti")
    #if course == "USO":
    #    mkdir(service, year_folder_id, "Test practic")
    #if course == "CNS" or course == "SIS":
    #    mkdir(service, year_folder_id, "Lectures")
    #    mkdir(service, year_folder_id, "Labs")
    #    mkdir(service, year_folder_id, "Assignments")
    #    mkdir(service, year_folder_id, "Exam")
    #    mkdir(service, year_folder_id, "Students")
    #if course == "SO2":
    #    mkdir(service, year_folder_id, "Curs")
    #    mkdir(service, year_folder_id, "Studenti")


if __name__ == '__main__':
    sys.exit(main())
# [END drive_quickstart]
