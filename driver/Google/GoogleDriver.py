# API: https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/index.html
import logging
import os

import httplib2
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from raid.RAIDStorage import RAIDStorage
from pydrive.files import GoogleDriveFile
from decimal import Decimal, getcontext


class GoogleDriver(RAIDStorage):
    FOLDER_ID = '0B3YfnXuRdcz4SXIyaXc2Z0xNQUE'


    def __init__(self):
        self.client = GoogleDrive(self.authorize())
        self.index = None


    def authorize(self):
        self.connected = False

        gauth = GoogleAuth()
        gauth.LoadCredentialsFile('credentials.json')

        try:
            if gauth.credentials is None:
                gauth.LocalWebserverAuth()
                self.connected = True
            elif gauth.access_token_expired:
                gauth.Refresh()
                self.connected = True
            else:
                gauth.Authorize()
                self.connected = True
        except httplib2.ServerNotFoundError:
            logging.critical('Connection could not be made to Google Drive')
            self.connected = False

        gauth.SaveCredentialsFile("credentials.json")
        return gauth


    def upload_file(self, file_name):
        file_list = self.client.ListFile({'q': "'0B3YfnXuRdcz4SXIyaXc2Z0xNQUE' in parents and trashed=false"}).GetList()
        matches = [i for i in file_list if i['title'] == file_name]

        if not matches:
            file = self.client.CreateFile({"parents": [{"kind": "drive#fileLink", "id": self.FOLDER_ID}]})
            file.SetContentFile(file_name)
            file.Upload()
            logging.warning("File Uploaded to Google")
        else:
            logging.error('Google: File already exists')


    def get_data(self, file_name):
        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + extention
        file_list = self.client.ListFile({'q': "'0B3YfnXuRdcz4SXIyaXc2Z0xNQUE' in parents and trashed=false"}).GetList()

        matches = [i for i in file_list if i['title'] == file_name]

        if not matches:
            logging.error('Google: No file found')
            return ('Google', self.index)
        else:
            file = matches[0]
            data = file.GetContentString(mimetype='text/csv').replace('\r\n', '')
            data = [data[i:i + 10] for i in range(0, len(data), 10)]
            return [file['title'], data]

        return matches[0]

    def delete_data(self, file_name):
        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + '.csv'
        file_list = self.client.ListFile(
            {'q': "'0B3YfnXuRdcz4SXIyaXc2Z0xNQUE' in parents and trashed=false"}).GetList()

        matches = [i for i in file_list if i['title'] == file_name]

        if not matches:
            logging.error("Google: No file found")
        else:
            try:
                file = matches[0]
                file.Delete()
                logging.warning("Google: File deleted")
                return True
            except:
                logging.error("Google: File could not be deleted")
                return False



    def remaining_storage(self):
        info = self.client.GetAbout()
        total_bytes = int(info['quotaBytesTotal'])
        used_bytes = int(info['quotaBytesUsed'])
        remaining_bytes = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(remaining_bytes) / Decimal(1073741824)
        return gb_val

    def check_connection(self):
        return self.connected
