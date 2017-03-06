from raid.RAIDFile import RAIDFile
from raid.RAIDStorage import RAIDStorage
import Box.BoxDriver as Box
import Google.GoogleDriver as Google
import Dropbox.DropboxDriver as Dropbox

bin_format = '#010b'


class RAID5:
    dbx = Dropbox.DropboxDriver()
    google = Google.GoogleDriver()
    box = Box.BoxDriver()

    files = []
    storage = []

    def __init__(self, storage):
        #self.num_storage = len(storage_details)
        self.num_storage = len(storage)
        self.storage = storage

    def __len__(self):
        return len(self.storage[0])  # Return the max capacity of our storage #ToDo - define a len for cloud drivers


    def get_stripe(self, index):  # Get the blocks of data from index on each drive

        block = []  # our block of bits

        for i in (len(self.storage)):
            data = self.storage[i].read_data(index)
            block.append(data)
            # ToDo - calculate padding

        return block


    def write_file(self, file):  # create internal representation of file and send bit too write
        if len(self.files) == 0:
            file.start_addr = 0
        else:
            file.start_addr = len(self.storage[0])

        print('Start adder = ', file.start_addr)

        self.files.append(file)

        print(type(file.binary_data[0]))
        blocks = list(RAID5.split_data(file.binary_data, len(self.storage) - 1))  # minus one drive to account for parity drive
        file.padding = (len(self.storage) - 1) - len(blocks[-1])  # calculate padding with
        print('Padding: ', file.padding)

        self.write_bits(file.binary_data + [format(0, bin_format)] * file.padding)  # write the binary data + the necessary 0 padding


    def write_bits(self, data):  # get data and split into blocks, calculate parity bit, insert and write

        blocks = RAID5.split_data(data, len(self.storage) - 1)  # minus one drive to account for parity drive
        bloc = []

        for b in blocks:
            bloc.append(b)
            # Calculate parity bit for block b & validate

            parity_bit = self.calculate_parity(b)
            self.validate_parity(b + [format(parity_bit, bin_format)])
            #print('Parity Validated')


            p_drive = self.calculate_parity_drive(len(self))

            # Insert the parity bit into the block at the position of the current parity disk
            b.insert(p_drive, format(parity_bit, bin_format))

            # Write block to disks
            for i in range(len(b)):
                self.storage[i].write(b[i])


    def read_file(self):  # read bits from non parity drive and reconstruct #todo - implement requesting block ids from storage
        ret_bits = []
        ret_files = []

        for i in range(len(self)):  # len(self) = len of disk[0]
            for j in range(self.num_storage):
                parity_disk = self.calculate_parity_drive(i)
                if j != parity_disk:
                    ret_bits.append(bytes(self.storage[j].read(i)))  # take all bits from non-parity disks
            for k in range(len(self.files)):  # len(self.files) = len of file list
                if i == self.files[k].start_addr - 1:
                    ret_bits = ret_bits[:len(ret_bits) - self.files[k - 1].padding]  # ret_bits = length of ret_bits - padding
                    ret_files.append(RAIDFile.from_bits(k - 1, ret_bits))
                    ret_bits = []

        ret_bits = ret_bits[:len(ret_bits) - self.files[-1].padding]
        ret_files.append(
            RAIDFile.from_bits(self.files[-1].id, 'test.txt', ret_bits))  # todo - figre out way to get file name
        return ret_files

    def read_bits(self):
        ret_bits = []
        for i in range(len(self)):
            for j in range(len(self.storage)):
                parity_disk = self.calculate_parity_drive(i)
                if j != parity_disk:
                    ret_bits.append(self.storage[j].read(i)[2:])

        return ret_bits

    def clean_binary(self, binary_data): #removes 0b formatting at start of block
        for i in range(len(binary_data)):
            binary_data[i] = binary_data[i][2:]

        return binary_data

    def read_all_files(self):
        ret_bits = []
        ret_files = []

        for i in range(len(self)):  # len(self) = len of disk[0]
            for j in range(self.num_storage):
                parity_disk = self.calculate_parity_drive(i)
                if j != parity_disk:
                    ret_bits.append(self.storage[j].read(i))  # take all bits from non-parity disks
            for k in range(len(self.files)):  # len(self.files) = len of file list
                if i == self.files[k].start_addr - 1:
                    ret_bits = ret_bits[
                               :len(ret_bits) - self.files[k - 1].padding]  # ret_bits = length of ret_bits - padding
                    ret_files.append(RAIDFile.from_bits(k - 1, ret_bits))
                    ret_bits = []

        ret_bits = ret_bits[:len(ret_bits) - self.files[-1].padding]
        ret_files.append(RAIDFile.from_bits(self.files[-1].id, 'test.txt', ret_bits)) #todo - figre out way to get file name
        return ret_files


    # Read all data on disks, ignoring parity bits and padding. Does not account for missing disks.
    def read_all_data(self):
        ret_str = ''
        for i in range(len(self)):
            for j in range(len(self.storage)):
                parity_disk = self.calculate_parity_drive(i)
                if j != parity_disk:
                    ret_str += chr(int(self.storage[j].read(i), 2))  # Convert bin string to integer, then to character
            for k in range(len(self.files)):
                if i == self.files[k].start_addr - 1:
                    ret_str = ret_str[:len(ret_str) - self.files[k - 1].padding]

        ret_str = ret_str[:len(ret_str) - self.files[-1].padding]
        return ret_str

    def calculate_parity_drive(self, index):
        return self.num_storage - ((index % self.num_storage) + 1)  # get chosen disk by geting the index mod the number of disks, add one to prevent it choosing a disk 0


    def check_connection(self):
        pass


    def reconstruct_drive(self, disk_num):
        print("Reconstructing Disk")
        if (self.num_disks - len(self.disks)) > 1:
            raise Exception("Cannot reconstruct disk: too many disks missing") #ToDo - create custom exception

        new_disk = RAIDStorage(disk_num, self.disk_cap)
        for i in range(len(self.disks[0])):
            block = []
            for j in range(len(self.disks)):
                block.append(self.disks[j].read(i))
            self.validate_parity(block + [format(self.calculate_parity(block), bin_format)])

            new_disk.write(format(self.calculate_parity(block), bin_format))
        self.disks.insert(disk_num, new_disk)
        self.validate_disks()


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
            calculated_parity = RAID5.calculate_parity(block)
            if calculated_parity != int(parity,2):
                raise Exception('placeholder')#raise ParityCalculationException(block, calculated_parity, int(parity, 2)) #ToDo - create custom exception
            block.insert(i, parity)


    @staticmethod
    def split_data(data, num_drives):  # split data into blocks for each drive
        for i in range(0, len(data), num_drives):  # iterate through data in chunks of the amount of storage units available
            yield data[i:i + num_drives]
