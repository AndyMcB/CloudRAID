from abc import abstractmethod


class RAIDStorage:

    def __init__(self, storage_id, capacity=0 ):
        self.storage_id = storage_id
        self.capacity = capacity
        self.data = []
        print(storage_id, capacity)

    def __repr__(self): ##ToDo - fix descriptor
        return repr(self.storage_id) + ":" + repr(self.data)

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @abstractmethod
    def write(self, data): #ToDo - add error handing to inheriting classes
        return
        # if (self.capacity > 0) and (len(self.data) + len(data) > self.capacity):
        #     raise Exception('Placeholder')#storageFullException(self.storage_id)
        # self.data.append(data)

    @abstractmethod
    def read(self, index): #ToDo - add error handling to inheriting class
        return
        # if index >= len(self.data):
        #     raise Exception("Cannot read index '" + repr(index) + "' on storage_driver '" + repr(self.storage_id) +"': Index out of bounds")
        # return self.data[index]

    @abstractmethod
    def remaining_storage(self):
        return