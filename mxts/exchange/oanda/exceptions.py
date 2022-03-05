class OandaException(Exception):
    """A base exception for all exceptions in the oanda package"""
    pass

class OandaWarning(Warning):
    """A base warning for all warnings in the oanda package"""
    pass

class InitializationFailure(OandaException):
    """OandaClient Failed to initialize"""
    pass

class ResponseTimeout(OandaException):
    """The server took to long to respond"""
    pass

class CloseAllTradesFailure(OandaException):
    """Failed to close all trades"""
    pass

class InvalidValue(OandaException):
    """A supplied value does not meet the specification of valid values"""
    pass

class InvalidFormatArguments(OandaException):
    """Arguments to format a DecimalNumber or PriceValue are invalid"""
    pass

class IncompatibleValue(OandaException):
    """A supplied argument is different than the predefined value"""
    pass

class UnknownKeywordArgument(OandaWarning):
    """A passed keyword argument is not in the objects __init__ signature"""
    pass

class InstantiationFailure(OandaException):
    """oanda was unable to create an object from the passed arguments"""
    pass

class UnexpectedStatus(OandaException):
    """The server returned an unexpected HTTP status"""
    pass

class FailedToCreatePath(OandaException):
    """Unable to construct the path for the requested endpoint"""
    pass

class InvalidOrderRequest(OandaException):
    """The order request is not with in the instruments specification the order is for"""
    pass