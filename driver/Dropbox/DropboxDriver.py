# Include the Dropbox SDK
import logging
import os

import requests
from json import dump, load
import dropbox
from os import path
from raid.RAIDStorage import RAIDStorage
from decimal import Decimal,getcontext

class DropboxDriver(RAIDStorage):

    auth_token = 'BNwX0RfADiAAAAAAAAAACTQkLma2JEPQSZc1zO0jN9c8RZl5fKLiY28xKQ10zzj2'
    app_key = 'fvwzhyjpgnsftzr'
    app_secret = 'bq2ahq4t4sbbsgu'
    access_token = '5MFjNoM22TgAAAAAAAAAUDpe6Jp9OgAkNy9JC-H9PQ4'


    def __init__(self):
        try:
            self.access_token = self.retrieve_tokens()
            self.client = dropbox.Dropbox(self.access_token)  # Dropbox Client Object
            self.index = None
            self.connected = self.check_connection()
        except:
            self.access_token, uid = self.get_access_token()
            self.store_tokens(self.access_token)
            self.client = dropbox.Dropbox(self.access_token)  # Dropbox Client Object
            self.index = None



    def upload_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_name = path.basename(file_path)
            file_path = "/FYP/{0}".format(file_name)
            try:
                self.client.files_upload(f.read(), file_path, mute=True)
                logging.warning("File uploaded to Dropbox")
            except dropbox.exceptions.ApiError:
                logging.error('Dropbox: File already exists')



    def get_data(self, file_name):
        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + extention

        file_path = "/FYP/{0}".format(file_name)
        print(file_path)
        file, response = self.client.files_download(file_path)

        data = response.content.decode('utf-8').replace('\r\n', '')
        data = [data[i:i + 10] for i in range(0, len(data), 10)]
        return [file.name, data]



    def get_access_token(self):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        auth_url = flow.start()
        res = requests.get(auth_url)
        print(res.url)
        print('Enter auth code below: ')
        code = input()
        access_token, user_id = flow.finish(code)
        return access_token, user_id


    def store_tokens(self, access_token):
        data = {'access_token': access_token}
        with open('dropbox_tokens.json', 'w', encoding='utf-8') as store:
            dump(data, store, ensure_ascii=False)


    def retrieve_tokens(self):
        with open('dropbox_tokens.json', 'r') as store:
            tokens = load(store)
        access =  tokens['access_token']
        return access

    def remaining_storage(self):
        info = self.client.users_get_space_usage()
        total_bytes = info.allocation.get_individual().allocated
        used_bytes = info.used
        remaining_bytes = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(remaining_bytes) / Decimal(1073741824)
        return gb_val


    def check_connection(self):
        try:
            self.client.users_get_current_account()  # test for connection ToDo improve
            return True
        except requests.exceptions.ConnectionError:
            logging.critical("Connection could not be made to Dropbox")
            return False