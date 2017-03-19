import sqlite3

bin_format = '#010b'

class RAIDFile:

    binary_data = []  # List of binary characters
    start_addr = None
    padding = 0
    file_name = ''

    def __init__(self, file_id, file_name, data, conn):
        self.start_addr = file_id
        self.data_S = data  # String to convert
        self.binary_data = self.convert_data(data)  # Binary version of string
        self.file_name = file_name
        self.db_add_file(conn, file_name)

    def __len__(self):
        return len(self.binary_data)

    def __repr__(self):  # toString
        return repr(self.id) + ": '" + self.data_S + "'"

    def __eq__(self, other):
        if type(other) is type(self):
            return self.binary_data == other.binary_data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def db_add_file(self, conn, file_name):
        try:
            conn.execute('INSERT INTO files VALUES (?, ?)', (file_name, 'test'))
            conn.commit()
        except sqlite3.IntegrityError:
            print('Error: File already exists on record')

    def db_remove_file(self, conn, file_name):
        conn.execute('DELETE FROM files  WHERE name=?', (file_name,))
        conn.commit()

    @staticmethod
    def convert_data(d):  # d = data string
        bin_list = []
        for x in d:  # for each letter in d
           bin_list.append(format(ord(x), bin_format))  # Change character -> integer -> binary string and append to list

        return bin_list

    @staticmethod
    def from_bits(file_id, file_name, b):  # inverse of convert string
        ret_str = ""
        for x in b:
            ret_str += chr(int(x, 2))
        return RAIDFile(file_id, file_name, ret_str)

    @staticmethod
    def from_name(file_name):  # inverse of convert string
        pass
