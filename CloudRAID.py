##Main Driver File
import Box.BoxDriver as Box
import Google.GoogleDriver as Google
import Dropbox.DropboxDriver as Dropbox

# ToDo - comment code
class CloudRAID:

    dbx = Dropbox.DropboxDriver()
    google = Google.GoogleDriver()
    box = Box.BoxDriver()


    def upload(self, file):
        self.dbx.uploadFile()
        self.google.uploadFile()
        self.box.upload()
        pass


    def strip(self):
        pass

    def reconstruct(self):
        pass