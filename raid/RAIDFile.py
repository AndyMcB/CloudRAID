

bin_format = '#010b'

class RAIDFile:

    binary_data = []  # List of binary characters
    start_addr = None
    padding = 0
    file_name = ''

    def __init__(self, file_id, file_name, data):
        self.id = file_id  # Numbering variable for the blocks to know what order they are in
        self.data_S = data  # String to convert
        self.binary_data = self.convert_data(data)  # Binary version of string
        self.file_name = file_name
        with open('file_record.txt', 'a') as records: #ToDo - expand record keeping detail
            records.write('\n' + file_name)

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

