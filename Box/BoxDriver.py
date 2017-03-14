import os

import requests
from json import dump, load
from boxsdk import Client
from boxsdk import OAuth2
from decimal import Decimal,getcontext

from Box.BoxOAuth2 import *
from boxsdk.network.default_network import DefaultNetwork
from pprint import pformat
from os import path
from urllib.parse import urlparse, parse_qs
from raid.RAIDStorage import RAIDStorage



class BoxDriver(RAIDStorage):

    # ToDo - factor out info into config file
    CLIENT_ID = 'y0vwgy93gan8sdalfr39vjblmvyb32xw'
    CLIENT_SECRET = 'WPIqt4wCxKykaq1ENozbpXElhqaMDPup'
    FOLDER_ID = '18839913719'  # ID of FYP folder in Box

    def __init__(self):
        self.access_token, self.refresh_token = self.retrieve_tokens()
        oauth2 = OAuth2(self.CLIENT_ID, self.CLIENT_SECRET, access_token= self.access_token, refresh_token= self.refresh_token, store_tokens=self.store_tokens)
        self.client = Client(oauth2)  # Create the SDK client
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
        self.client.folder(self.FOLDER_ID).upload(file_path, file_name, preflight_check=True)

    def get_data(self,file_name):
        name, extention = os.path.splitext(file_name)
        file_name = name + self.index + extention

        search_results = self.client.search(
            file_name,
            limit=2,
            offset=0,
            ancestor_folders=[self.client.folder(folder_id=self.FOLDER_ID)]
            #file_extensions=['txt'],
        )
        for item in search_results:
            item_with_name = item.get(fields=['name'])
            print('matching item: ' + item_with_name.id + '-' + item_with_name.name + '\n' )

        data = item_with_name.content().decode('utf-8').replace('\r\n', '')
        data = [data[i:i + 10] for i in range(0, len(data), 10)]
        return [item_with_name.name, data]

    def remaining_storage(self):
        info = self.client.user(user_id='me').get()
        total_bytes = info.space_amount
        used_bytes = info.space_used
        storage_remaining = total_bytes - used_bytes
        getcontext().prec = 3
        gb_val = Decimal(storage_remaining) / Decimal(1073741824)
        return gb_val



class LoggingNetwork(DefaultNetwork):
    def request(self, method, url, access_token, **kwargs):
        """ Base class override. Pretty-prints outgoing requests and incoming responses. """
        print('\x1b[36m{} {} {}\x1b[0m'.format(method, url, pformat(kwargs)))
        response = super(LoggingNetwork, self).request(
            method, url, access_token, **kwargs
        )
        if response.ok:
            print('\x1b[32m{}\x1b[0m'.format(response.content))
        else:
            print('\x1b[31m{}\n{}\n{}\x1b[0m'.format(
                response.status_code,
                response.headers,
                pformat(response.content),
            ))
        return response




        ##Get new tokens
        # try: #Try retrieve from token store and refresh
        # token_dict = BoxOAuth2().oauth2_token_request(self.refresh_token)          ###Find way to detect if we need to refresh the tokens
        # self.access_token = token_dict['access_token']
        # self.refresh_token = token_dict['refresh_token']
        # except BoxAuthenticationException:
        # self.access_token, self.refresh_token = oauth2.authenticate(self.get_auth_code(oauth2))
