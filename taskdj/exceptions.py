class TaskdError(Exception):
    pass

class StatusError(TaskdError):
    """
    Raised when a taskd status value is invalid. 
    Valid status values are: pending, deleted, completed, waiting, and recurring.
    """
    pass

class TaskdConnectionError(TaskdError):
    pass
