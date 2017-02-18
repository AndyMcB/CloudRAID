# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from os import path

class GoogleDriver:

    FOLDER_ID = '0B3YfnXuRdcz4SXIyaXc2Z0xNQUE'

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile('credentials.json')

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")

    def __init__(self):
        self.client = GoogleDrive(self.gauth)

    def uploadFile(self, file_name):
        file = self.client.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.FOLDER_ID}]})
        file.SetContentFile(file_name)
        file.Upload()