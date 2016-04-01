# -*- coding: utf-8 -*-
class NetworkZeroError(Exception): 
    pass

class SocketAlreadyExistsError(NetworkZeroError): 
    pass

class SocketTimedOutError(NetworkZeroError): 
    pass

class InvalidAddressError(NetworkZeroError):
    pass