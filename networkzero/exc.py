# -*- coding: utf-8 -*-
"""Common exceptions for networkzero
"""
class NetworkZeroError(Exception): 
    pass

class SocketAlreadyExistsError(NetworkZeroError): 
    pass

class SocketTimedOutError(NetworkZeroError): 
    pass

class InvalidAddressError(NetworkZeroError):
    pass