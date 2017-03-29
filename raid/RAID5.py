import base64
import itertools
import logging
import sys
import time
from threading import Thread

import driver.Dropbox.DropboxDriver as Dropbox
import driver.Google.GoogleDriver as Google

import driver.Box.BoxDriver as Box
from raid.RAIDFile import RAIDFile

bin_format = '#010b'


class RAID5:
    dbx = Dropbox.DropboxDriver()
    google = Google.GoogleDriver()
    box = Box.BoxDriver()

    files = []
    storage_driver = []

    def __init__(self, storage_driver):
        self.num_storage = len(storage_driver)
        self.storage_driver = storage_driver
        self.calculate_drive_index()

    def __len__(self):  # Returns smallest amount of storage_driver available
        return len(self.storage_driver)

    def calculate_drive_index(self):
        p_drive = self.calculate_parity_drive(len(self))
        self.storage_driver.index_drives(p_drive)

    def write_file(self, file, file_name):  # create internal representation of file and send bit too write
        if len(self.files) == 0:
            file.start_addr = 0
        else:
            file.start_addr = len(self.storage_driver)

        self.files.append(file)

        logging.warning(" splitting data...")

        blocks = list(RAID5.split_data(file.binary_data, len(self.storage_driver) - 1))  # minus one drive to account for parity drive
        file.padding = (len(self.storage_driver) - 1) - len(blocks[-1])  # calculate padding with

        self.write_bits(file.binary_data + [format(0, bin_format)] * file.padding,
                        file_name)  # write the binary data + the necessary 0 padding

    def write_bits(self, data, file_name):  # get data and split into blocks, calculate parity bit, insert and write

        blocks = RAID5.split_data(data, len(self.storage_driver) - 1)  # minus one drive to account for parity drive


        logging.warning(" calculating parity and generating bit load")
        cur_milli_time = lambda: int(round(time.time() * 1000))
        start_time = cur_milli_time()

        thread = Thread(target=self.spinner, )
        self.spin = True
        thread.start()
        for b in blocks:
            # Calculate parity bit for block b & validate
            parity_bit = self.calculate_xor(b)
            b.append(parity_bit)
            self.validate_parity(b)
            p_drive = self.calculate_parity_drive(len(self))
            self.storage_driver.write(b, p_drive, file_name) #write to fle


        end = cur_milli_time()
        logging.warning("File processed & wrote in {} seconds".format((end - start_time)/1000))
        #logging.warning("File wrote in {} seconds".format((end_write - start_time)/1000))

        self.spin = False
        thread.join()
        logging.warning(' uploading blocks to storage')
        self.storage_driver.upload_blocks(file_name)

        end_time = cur_milli_time()
        logging.warning("File uploaded in {} seconds".format((end_time - start_time)/1000))

    def spinner(self):
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        while self.spin:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\r')

    def rebuild_txt_file(self, data, file_name):

        for name, bytes in data:  # ToDo - improve extensibility
            if '_p' not in name:
                if '_1' in name:
                    bloc1 = bytes
                else:
                    bloc2 = bytes

        data = [j for i in zip(bloc2, bloc1) for j in i]

        contents = []
        try:
            for i in data:
                contents.append(chr(int(str(i), 2)))
        except ValueError:
            logging.error('Byte error found')

        with open('downloads/'+file_name + '_rebuild.txt', 'w') as rebuild:

            for char in contents:
                try:
                    #rebuild.write(''.join(char))
                    rebuild.write(char)
                except UnicodeEncodeError:
                    logging.error('Unicode error found')

    def rebuild_img_file(self, data, file_name):

        for name, bytes in data:  # ToDo - improve extensibility
            if '_p' not in name:
                if '_1' in name:
                    bloc1 = bytes
                else:
                    bloc2 = bytes

        data = [j for i in zip(bloc2, bloc1) for j in i]
        file = self.from_bits(1, file_name, data)

        file_name = file_name + '_rebuild.jpg'
        with open('downloads/'+file_name, 'wb') as f: #ToDo - fix hardcoded name
            d = base64.b64decode(file.data)
            f.write(d)

    def reconstruct_txt_from_parity(self, data, file_name, corrupted_drive ):  ##ToDO- potentially refactor into origional two functions as error case
        logging.warning('Rebuilding file from parity data')
        for name, bytes in data:
            if corrupted_drive not in name:
                if '_p' in name:
                    p_bloc = bytes
                else:
                    d_bloc = bytes

        recov = []
        for b in zip(p_bloc, d_bloc):
            recov.append(RAID5.calculate_xor(b))

        if corrupted_drive == '_0':
            data = [j for i in zip(recov, d_bloc) for j in i]
        elif corrupted_drive == '_1':
            data = [j for i in zip(d_bloc, recov) for j in i]

        contents = []
        try:
            for i in data:
                contents.append(chr(int(str(i), 2)))
        except ValueError:
            logging.error('Byte error found')

        with open('downloads/'+file_name + '_rebuild.txt', 'w') as rebuild:
            for char in contents:
                try:
                    rebuild.write(''.join(char))
                except UnicodeEncodeError:
                    logging.error('Unicode error found')

    def reconstruct_img_from_parity(self, data, file_name, corrupted_drive='_0'):  ##ToDO- potentially refactor into origional two functions as error case
        logging.warning('Rebuilding file from parity data')
        for name, bytes in data:
            if corrupted_drive not in name:
                if '_p' in name:
                    p_bloc = bytes
                else:
                    d_bloc = bytes

        recov = []
        for b in zip(d_bloc, p_bloc):
            recov.append(RAID5.calculate_xor(b))

        data = [j for i in zip(recov, d_bloc) for j in i]

        contents = []
        try:
            for i in data:
                contents.append(chr(int(str(i), 2)))
        except ValueError:
            logging.error('Byte error found')

        file_name = file_name + '_rebuild.jpg'
        file = self.from_bits(1, file_name, data)
        with open('downloads/'+file_name, 'wb') as f:  # ToDo - fix hardcoded name
            d = base64.b64decode(file.data)
            f.write(d)

    def from_bits(self, file_id, file_name, b):  # inverse of convert string
        ret_str = ""
        for x in b:
            ret_str += chr(int(x, 2))
        return RAIDFile(file_id, None, ret_str, binary_data=0, file_name=file_name)


    def calculate_parity_drive(self, index):
        return self.num_storage - ((index % self.num_storage) + 1)

    def check_connection(self):
        pass # ToDO implement

    @staticmethod
    def calculate_xor(block):
        try:
            b1 = block[0]
            b2 = block[1]
            return format((int(b1, 2) ^ int(b2, 2)), '#010b')
        except ValueError:
            logging.error("Invalid Byte")


    # Calculate parity bit for block. We need to convert the bin strings to integers in order to use bit
    # manipulation to calculate the XOR
    @staticmethod
    def calculate_parity(block):
        calculated_parity = None
        for x in block:  # calc parity = XOR c_p and int x, base 2 else c_p = int x, base 2
            calculated_parity = calculated_parity ^ int(x, 2) if calculated_parity is not None else int(x, 2)
        return calculated_parity

    # Validates the parity of a block by removing each item in sequence, calculating the parity of the remaining items,
    # and comparing the result to the removed item.
    @staticmethod
    def validate_parity(block):
        for i in range(len(block)):
            parity = block.pop(i)
            calculated_parity = RAID5.calculate_xor(block)
            if calculated_parity != parity:
                raise Exception(
                    'placeholder')  # raise ParityCalculationException(block, calculated_parity, int(parity, 2)) #ToDo - create custom exception
            block.insert(i, parity)

    @staticmethod
    def split_data(data, num_drives):  # split data into blocks for each drive
        for i in range(0, len(data),
                       num_drives):  # iterate through data in chunks of the amount of storage_driver units available
            yield data[i:i + num_drives]
