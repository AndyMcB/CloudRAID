# Include the Dropbox SDK
import dropbox


class DropboxDriver:

    dbx = dropbox.Dropbox('BNwX0RfADiAAAAAAAAAACTQkLma2JEPQSZc1zO0jN9c8RZl5fKLiY28xKQ10zzj2')  # Dropbox Client Object
    print(dbx.users_get_current_account())
    app_key = 'k94xie299aa220o'
    app_secret = 'k94xie299aa220o'


    def __init__(self):
        pass

    def uploadFile(self, client, file_name):
        with open(file_name, 'rb') as f:
            filePath = "/{0}".format(file_name)
            client.files_upload(f.read(), filePath, mute=True)
