##Main Driver File
import _csv
import logging
import os

import httplib2
import requests

import driver.Dropbox.DropboxDriver as Dropbox
import driver.Google.GoogleDriver as Google

import driver.Box.BoxDriver as Box


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


    def write(self, block, p_drive, file_name):

        if len(self.drivers) != len(block): raise Exception('Num blocks does not match num disks')
        f_name, ext = os.path.splitext(file_name)

        for i in range(len(block)):
            if i == p_drive:
                name = f_name + '_p.csv'
                with open(name, 'a', newline='') as csv:
                    writer = _csv.writer(csv, delimiter=',')
                    b = block[i]
                    writer.writerow([b])
            else:
                name = f_name + '_' + str(i) + '.csv'
                with open(name, 'a', newline='') as csv:
                    writer = _csv.writer(csv, delimiter=',')
                    b = block[i]
                    writer.writerow([b])


    def upload_blocks(self, file_name):
        f_name, ext = os.path.splitext(file_name)
        payload = os.path.getsize(f_name + '_0.csv')
        logging.warning("File Payload is {} kilobytes".format(payload / 1000))

        self.dbx.upload_file(f_name + '_0.csv')
        self.google.upload_file(f_name + '_1.csv')
        self.box.upload_file(f_name + '_p.csv')
        os.remove(f_name + '_0.csv')
        os.remove(f_name + '_1.csv')
        os.remove(f_name + '_p.csv')


    def download_blocks(self, file_name):
        d1, d2, d3 = None, None, None

        try:
            d1 = self.google.get_data(file_name + '.csv')
            d2 = self.dbx.get_data(file_name + '.csv')
            d3 = self.box.get_data(file_name + '.csv')

            return [d1, d2, d3]

        except FileNotFoundError:
            ret = [type(d1), type(d2), type(d3)]
            for x in ret:
                if x is None:
                    raise FileNotFoundError

                    ##ToDo - add retry queue
    def delete(self, file_name):
        d1 = self.google.delete_data(file_name)
        d2 = self.dbx.delete_data(file_name)
        d3 = self.box.delete_data(file_name)
        returns = [d1, d2, d3]

        if returns.count(True) == 3:
            logging.warning('File deleted from all providers')
            return []
        elif returns.count(True) < 2:
            logging.critical("File could not be deleted from all providers. \n\t It may have been deleted previously")
            down = [i for i in enumerate(returns) if i[1] is False]
            for entry in down:
                if 'Google' in entry:
                    down[0] += ('Google',)
                    logging.critical("Cannot delete from Google.")
                if 'Dropbox' in entry:
                    down[1] += ('Dropbox',)
                    logging.critical("Cannot delete from Dropbox")
                if Box in entry:
                    down[2] += ('Box',)
                    logging.critical("Cannot delete from Box")
            return down



    def remaining_storage(self):

        remaining = []
        try:
            d_storage = str(self.dbx.remaining_storage())+' GB', 'Dropbox'
        except requests.exceptions.ConnectionError:
            d_storage = 'Dropbox Unavailable'

        try:
            g_storage = str(self.google.remaining_storage())+' GB', 'Google'
        except httplib2.ServerNotFoundError:
            g_storage = 'Google Unavailable'
        try:
            b_storage = str(self.box.remaining_storage())+' GB', 'Box'
        except requests.exceptions.ConnectionError:
           b_storage = 'Box Unavailable'

        remaining.append(d_storage)
        remaining.append(g_storage)
        remaining.append(b_storage)
        return remaining





    def upload(self, file_path):  # depreciated - test uses only
        self.dbx.upload_file(file_path)
        self.google.upload_file(file_path)
        self.box.upload_file(file_path)


    def check_connection(self):
        """
        checks the connections to all providers
        1 - Google Drive
        2 - Dropbox
        3 - Box
        :return: list of numbers corresponding to downed connections
        empty list indicates all connections have been made
        """
        connections = [self.google.check_connection(), self.dbx.check_connection(), self.box.check_connection()]

        if connections.count(True) == 3:
            logging.warning(' All connections OK. System can be used for reads and writes.')
            return []
        elif connections.count(True) == 2:
            logging.critical("\nOnly two connections available. System only usable for reads")
            down = [i for i in enumerate(connections) if i == False ]
            if 0 in down:
                pass
                #logging.critical("Cannot connect to Google.")
            if 1 in down:
                pass
                #logging.critical("Cannot connect to Dropbox")
            if 2 in down:
                pass
                ##logging.critical("Cannot connect to Box")
            return down
        elif connections.count(True) < 2:
            logging.critical("Sufficient connections could not be made. System unsuitable for reads or writes.")
            down = [i for i in enumerate(connections) if i[1] == False]
        for entry in down:
                if 0 == entry[0]:
                    down[0] += ('Google',)
                    #logging.critical("Cannot connect to Google.")
                if 1 == entry[0]:
                    down[1] += ('Dropbox',)
                    #logging.critical("Cannot connect to Dropbox")
                if 2 == entry[0]:
                    down[2] += ('Box',)
                    #logging.critical("Cannot connect to Box")
        return down
