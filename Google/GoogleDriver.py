# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class GoogleDriver:

    FOLDER_ID = '0B3YfnXuRdcz4SXIyaXc2Z0xNQUE'

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()

    drive = GoogleDrive(gauth)

    def __init__(self):
        pass

    def uploadFile(self, client, file_name):
        file = client.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.FOLDER_ID}]})
        file.SetContentFile(file_name)
        file.Upload()