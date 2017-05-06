from abc import abstractmethod


class RAIDStorage:

    def __init__(self, storage_id, capacity=0 ):
        self.storage_id = storage_id
        self.capacity = capacity
        self.data = []


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
    def remaining_storage(self):
        return

    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def delete_data(self):
        pass