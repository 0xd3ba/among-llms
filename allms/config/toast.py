class ToastConfiguration:
    """ Class holding constants for toasts """
    type_information: str = "information"
    type_warning: str = "warning"
    type_error: str = "error"

    timeout: float = 2.0  # How long (in seconds) a toast is displayed on the screen
