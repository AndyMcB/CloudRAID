##Main Driver File
import Box.BoxDriver as Box
import Google.GoogleDriver as Google
import Dropbox.DropboxDriver as Dropbox

# ToDo - comment code
##TODO - Deal with app looking for files from where main file was called
class CloudRAID:

    dbx = Dropbox.DropboxDriver()
    google = Google.GoogleDriver()
    box = Box.BoxDriver()

    def __init__(self):
        pass

    def upload(self, file_path):
        self.dbx.uploadFile(file_path)
        self.google.uploadFile(file_path)
        self.box.uploadFile(file_path)
        pass


    def strip(self):
        pass

    def reconstruct(self):
        pass