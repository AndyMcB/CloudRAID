import base64
import sqlite3, os, logging

bin_format = '#010b'

class RAIDFile:

    binary_data = []  # List of binary characters
    start_addr = None
    padding = 0
    file_name = ''


    def __init__(self, file_id, file_metadata, data = None, binary_data = None, conn=None):
        if conn is not None:
            try:
                logging.warning('Adding record to DB')
                self.db_add_file(conn, file_metadata)
            except sqlite3.IntegrityError:
                logging.error('Error: File already exists on record')
                return None
        else:
            logging.error('No DB object found. Files will not be recorded.')

        self.start_addr = file_id
        self.data = data  # data to binerize
        self.file_name = file_metadata['full_name']
        if binary_data is None:
            logging.warning('Binarizing Data')
            self.binary_data = self.convert(self.file_name, data)  # Binary version of string


    def __len__(self):
        return len(self.binary_data)

    def __repr__(self):  # toString
        return repr(self.file_name)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.binary_data == other.binary_data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def db_add_file(self, conn, file_metadata):
        conn.execute('INSERT INTO files VALUES (?, ?, ?, ?, ?)',
                   (file_metadata['full_name'], file_metadata['name'], file_metadata['file_type'],
                    file_metadata['size'], file_metadata['date_added']))
        conn.commit()



    def convert(self, file_name, data):
        fname, extention = os.path.splitext(file_name)
        if extention in ['.txt', '.csv']:
            logging.warning(' txt file detected ')
            return RAIDFile.convert_txt_data(data.decode('utf-8'))
        elif extention in ['.jpg', '.png']:
            logging.warning(' image file detected ')
            return RAIDFile.convert_img_data(base64.b64encode(data))
        else:
            raise Exception("File Type Not Supported") #ToDo - Make dedicated error

    @staticmethod
    def db_remove_file(conn, file_name):
        conn.execute('DELETE FROM files  WHERE full_name=?', (file_name,))
        conn.commit()

    @staticmethod
    def convert_txt_data(d):  # d = data string
        logging.info("converting txt data")
        bin_list = []
        for x in d:  # for each letter in d
           bin_list.append(format(ord(x), bin_format))  # Change character -> integer -> binary string and append to list

        return bin_list

    @staticmethod
    def convert_img_data(d):  # d = data string
        logging.info("converting img data")
        bin_list = []
        for x in d:  # for each letter in d
            bin_list.append(format(x, bin_format))  # Change character -> integer -> binary string and append to list

        return bin_list
    @staticmethod
    def from_bits(file_id, file_name, b):  # inverse of convert string
        logging.info('Converting bits')
        ret_str = ""
        for x in b:
            ret_str += chr(int(x, 2))
        return RAIDFile(file_id, file_name, ret_str)

