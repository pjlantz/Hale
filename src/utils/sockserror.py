#
# Socks Errors
#

class SocksException (Exception):
    """ Class descendants are raised for every fatal error that leads to
        connection close.
    """

class UnexpectedDataError (SocksException):
    pass

class UnhandledStateError (SocksException):
    pass

class LoginTooLongError (SocksException):
    """ According to RFC1929 Login must be 1-255 chars. """

class PasswordTooLongError (SocksException):
    """ According to RFC1929 Password must be 1-255 chars. """

class UnknownMethod (SocksException):
    """ Method is invalid or not implemented. """

class ConnectError (SocksException): 
    """ One of error replies after client issue CONNECT command. """

class UnhandledData (SocksException): 
    """ Server returned data that was not handled properly in our impl. """

class GlobalTimeoutError (SocksException): 
    """ Connection took too long and was interrupted unconditionally. """

# here are SOCKS error codes according to RFC1928
#
SOCKS_errors = [\
    "general SOCKS server failure",
    "connection not allowed by ruleset",
    "Network unreachable",
    "Host unreachable",
    "Connection refused",
    "TTL expired",
    "Command not supported",
    "Address type not supported"]

SOCKS4_errors = {\
    0x90: "No error",
    0x91: "Rejected or failed",
    0x92: "Connection to client ident refused",
    0x93: "Client login and ident reply mismatch"
}

#--- END ---



