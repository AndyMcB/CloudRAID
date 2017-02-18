# Include the Dropbox SDK
import requests
from json import dump, load
import dropbox
from os import path

class DropboxDriver:

    auth_token = 'BNwX0RfADiAAAAAAAAAACTQkLma2JEPQSZc1zO0jN9c8RZl5fKLiY28xKQ10zzj2'
    app_key = 'fvwzhyjpgnsftzr'
    app_secret = 'bq2ahq4t4sbbsgu'
    access_token = '5MFjNoM22TgAAAAAAAAAUDpe6Jp9OgAkNy9JC-H9PQ4'


    def __init__(self):
        try:
            self.access_token = self.retrieve_tokens()
            self.client = dropbox.Dropbox(self.access_token)  # Dropbox Client Object
        except:
            self.access_token, uid = self.get_access_token()
            self.store_tokens(self.access_token)
            self.client = dropbox.Dropbox(self.access_token)  # Dropbox Client Object
        self.uploadFile('test.txt')


    def uploadFile(self, file_path):
        with open(file_path, 'rb') as f:
            file_name = path.basename(file_path)
            filePath = "/FYP/{0}".format(file_name)
            self.client.files_upload(f.read(), filePath, mute=True)


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
        return access[0]