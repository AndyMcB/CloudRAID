

class RAID5:


    def __init__(self):
        pass


    def split_data(self): # split data into blocks for each disk
        pass


    def get_stripe(self, index): # Get the blocks of data from index on each disk
        pass


    def write_file(self, file): #set start address, appent to file list, get blocks, create padding and write
        pass


    def write_bits(self, data): # get data and split into blocks, calculate parity bit, insert and write
        pass


    def read_file(self): #read bits from non parity disk and reconstruct
        pass



    def reconstruct_disk(self):
        pass


    def calculate_parity_disk:
        pass


    def calculate_parity(self):
        pass


    def validate_parity(self): # provide parity check for block
        pass
