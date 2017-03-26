
class BoxClientException(Exception):
    def __init__(self, status_code, message=None, **kwargs):
        super(BoxClientException, self).__init__(message)
        self.status_code = status_code
        self.message = message
        self.__dict__.update(kwargs)

class BoxAuthenticationException(BoxClientException):
    pass
