class TaskdError(Exception):
    pass

class TaskdConnectionError(TaskdError):
    pass

class TaskdConfigError(TaskdError):
    pass
