# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from raid.RAIDStorage import RAIDStorage
from pydrive.files import GoogleDriveFile
from decimal import Decimal,getcontext

class GoogleDriver(RAIDStorage):

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
        self.index = None

    def upload_file(self, file_name):
        file = self.client.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.FOLDER_ID}]})
        file.SetContentFile(file_name)
        file.Upload()

    def get_data(self, file_name): #ToDo - Add error handling

        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + extention

        file_list = self.client.ListFile({'q': "'0B3YfnXuRdcz4SXIyaXc2Z0xNQUE' in parents and trashed=false"}).GetList()


        for file in file_list:
            print(file['title'])
            print(file_name)
            print(file['title'] == file_name)
            if file['title'] == file_name:
                data = file.GetContentString(mimetype='text/csv').replace('\r\n', '')
                data = [data[i:i + 10] for i in range(0, len(data), 10)]
                return [file['title'], data]

        raise Exception("No file found")

    def remaining_storage(self):
        info = self.client.GetAbout()
        total_bytes = int(info['quotaBytesTotal'])
        used_bytes = int(info['quotaBytesUsed'])
        remaining_bytes = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(remaining_bytes) / Decimal(1073741824)
        return gb_val
