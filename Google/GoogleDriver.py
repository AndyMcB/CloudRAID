# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from raid.RAIDStorage import RAIDStorage
import pprint
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

    def uploadFile(self, file_name):
        file = self.client.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.FOLDER_ID}]})
        file.SetContentFile(file_name)
        file.Upload()

    def remaining_storage(self):
        info = self.client.GetAbout()
        total_bytes = int(info['quotaBytesTotal'])
        used_bytes = int(info['quotaBytesUsed'])
        remaining_bytes = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(remaining_bytes) / Decimal(1073741824)
        return gb_val
