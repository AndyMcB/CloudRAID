import logging
import os, requests
from decimal import Decimal,getcontext
from json import dump, load
from os import path
from pprint import pformat
from urllib.parse import urlparse, parse_qs

from boxsdk import *
from boxsdk import exception
from boxsdk.network.default_network import DefaultNetwork

from driver.Box.BoxOAuth2 import *
from raid.RAIDStorage import RAIDStorage



class BoxDriver(RAIDStorage):

    CLIENT_ID = 'y0vwgy93gan8sdalfr39vjblmvyb32xw'
    CLIENT_SECRET = 'WPIqt4wCxKykaq1ENozbpXElhqaMDPup'
    FOLDER_ID = '18839913719'  # ID of FYP folder in Box

    def __init__(self):
        self.access_token, self.refresh_token = self.retrieve_tokens()
        oauth2 = OAuth2(self.CLIENT_ID, self.CLIENT_SECRET, access_token= self.access_token, refresh_token= self.refresh_token, store_tokens=self.store_tokens)
        self.client = Client(oauth2)  # Create the SDK client
        self.connected = self.check_connection()
        self.index = None
        #self.user_info(self.client)

    def get_auth_code(self, oauth2):
        auth_url, csrf_token = oauth2.get_authorization_url('http://localhost:8000')
        state = parse_qs(urlparse(auth_url).query)['state'][0]
        assert state == csrf_token
        res = requests.get(auth_url)
        print(res.url)
        print('Enter auth code below: ')
        code = input()
        return code

    def store_tokens(self, access_token, refresh_token):
        data = {'access_token': access_token,
                'refresh_token': refresh_token}

        with open('box_tokens.json', 'w', encoding='utf-8') as store:
            dump(data, store, ensure_ascii=False)

    def update_tokens(self):
        grant_type = 'refresh_token'
        box = BoxOAuth2()
        auth = box.oauth2_token_request(self.refresh_token)
        self.store_tokens(auth['access_token'], auth['refresh_token'])

    def retrieve_tokens(self):
        with open('box_tokens.json', 'r') as store:
            tokens = load(store)

        access =  tokens['access_token']
        refresh =  tokens['refresh_token']
        return access, refresh

    # Get current user details and display
    def user_info(self, client):
        current_user = client.user(user_id='me').get()
        print('Box User:', current_user.name)

    # Upload a file to Box!
    def upload_file(self, file_path):
        file_name = path.basename(file_path)
        try:
            self.client.folder(self.FOLDER_ID).upload(file_path, file_name, preflight_check=True)
            logging.warning("File Uploaded to Box")
        except exception.BoxAPIException:
            logging.error('Box: Filename in use')

    def delete_data(self, file_path):
        name, ext = os.path.splitext(path.basename(file_path))
        file_name = name + self.index + '.csv'
        try:
            items = self.client.folder(self.FOLDER_ID).get_items(limit=5)
            for file in items:
                if file.name == file_name:
                    file.delete()
                    logging.warning("Box: File deleted")
                    return True

            logging.warning("Box: File Not Found")
            return False
        except exception.BoxAPIException:
            logging.error('Box: File not found')
            return False


    def get_data(self,file_name):
        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + extention

        search_results = self.client.search(
            file_name,
            limit=2,
            offset=0,
            ancestor_folders=[self.client.folder(folder_id=self.FOLDER_ID)]
        )


        for item in search_results:
            if item.name == file_name:
                item_with_name = item.get(fields=['name'])
                data = item_with_name.content().decode('utf-8').replace('\r\n', '')
                data = [data[i:i + 10] for i in range(0, len(data), 10)]

                return [item_with_name.name, data]

        logging.error('Box: File not found')
        return ('Box', self.index)

    def check_connection(self):
        try:
            self.client.user().get() #See if the user data can be retrieved
            return True
        except requests.exceptions.ConnectionError:
            #logging.critical("Connection could not be made to Box")
            return False


    def remaining_storage(self):
        info = self.client.user(user_id='me').get()
        total_bytes = info.space_amount
        used_bytes = info.space_used
        storage_remaining = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(storage_remaining) / Decimal(1073741824)
        return gb_val



