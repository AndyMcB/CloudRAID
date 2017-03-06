##Main Driver File
import Box.BoxDriver as Box
import Google.GoogleDriver as Google
import Dropbox.DropboxDriver as Dropbox


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


    def strip(self):
        pass

    def reconstruct(self):
        pass

    def remaining_storage(self):

        remaining = []
        d_storage = self.dbx.remaining_storage()
        g_storage = self.google.remaining_storage()
        b_storage = self.box.remaining_storage()

        remaining.append(d_storage, g_storage, b_storage)
        return remaining