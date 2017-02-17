import io
from boxsdk import Client
from boxsdk import OAuth2
from Box import BoxOAuth2

class BoxDriver:

    #ToDo -
    CLIENT_ID = 'y0vwgy93gan8sdalfr39vjblmvyb32xw'
    CLIENT_SECRET = 'WPIqt4wCxKykaq1ENozbpXElhqaMDPup'
    REFRESH_TOKEN = ''
    FOLDER_ID = '18839913719'  # ID of FYP folder in Box

    oauth2 = OAuth2(CLIENT_ID, CLIENT_SECRET)  # access_token=ACCESS_TOKEN

    def __init__(self):
        pass

    #ToDo - add check for tokens being out of date
    def updateTokens(self, client_id, client_secret, refresh_token):
        grant_type = 'refresh_token'
        auth = BoxOAuth2._oauth2_token_request(client_id, client_secret, grant_type, refresh_token)
        self.REFRESH_TOKEN = auth['refresh_token']
        self.ACCESS_TOKEN = auth['access_token']
        print(auth['refresh_token'])
        print(auth['access_token'])


    # Create the SDK client
    client = Client(oauth2)


    # Get current user details and display
    def userInfo(self, client):
        current_user = client.user(user_id='me').get()
        print('Box User:', current_user.name)


    # Upload a file to Box!
    def uploadFile(self, client, file):
        stream = io.StringIO()
        stream.write('Box Python SDK test!')
        stream.seek(0)
        print(client.folder(self.FOLDER_ID).get())
        client.folder(self.FOLDER_ID).upload_stream(stream, file)





