##Main Driver File
import Box.BoxDriver as Box
import Google.GoogleDriver as Google
import Dropbox.DropboxDriver as Dropbox
import _csv, os

##ToDo - Add logging

##TODO - Deal with app looking for files from where main file was called
class CloudRAID:

    dbx = Dropbox.DropboxDriver()
    google = Google.GoogleDriver()
    box = Box.BoxDriver()
    drivers = []

    def __init__(self):
        self.drivers.append(self.dbx)
        self.drivers.append(self.google)
        self.drivers.append(self.box)
        self.count = 0


    def __len__(self):
        return len(self.drivers)

    def index_drives(self, p_drive):
        for i in range(len(self.drivers)):
            if i == p_drive:
                self.drivers[i].index = '_p'
            else:
                self.drivers[i].index = '_{0}'.format(i)

    def write(self, block, p_drive): ##ToDo- look into dedicated db for recored (posible to elastic searchize)

        if len(self.drivers) != len(block): raise Exception('Num blocks does not match num disks')

        for i in range(len(block)):
            if i == p_drive:
                name = 'data_p.csv'
                with open(name, 'a', newline='') as csv:
                    writer = _csv.writer(csv, delimiter=',')
                    b =  block[i]
                    writer.writerow([b])
            else:
                name = 'data_' + str(i) + '.csv'
                with open(name, 'a', newline='') as csv:
                    writer = _csv.writer(csv, delimiter=',')
                    b = block[i]
                    writer.writerow([b])


    def upload_blocks(self): ##ToDo - dehardcode #ToDo - Dynamically get names
        self.dbx.upload_file('data_0.csv')
        self.google.upload_file('data_1.csv')
        self.box.upload_file('data_p.csv')
        os.remove('data_0.csv')
        os.remove('data_1.csv')
        os.remove('data_p.csv')


    def read(self):
        pass


    def download_blocks(self, file_name):
        d1 = self.google.get_data(file_name)
        d2 = self.dbx.get_data(file_name)
        d3 = self.box.get_data(file_name)

        return [d1, d2, d3]




    def reconstruct(self):
        pass

    def remaining_storage(self):

        remaining = []
        d_storage = self.dbx.remaining_storage()
        g_storage = self.google.remaining_storage()
        b_storage = self.box.remaining_storage()

        remaining.append(d_storage)
        remaining.append(g_storage)
        remaining.append(b_storage)
        return remaining


    def upload(self, file_path): #depreciated - test uses only
        self.dbx.upload_file(file_path)
        self.google.upload_file(file_path)
        self.box.upload_file(file_path)