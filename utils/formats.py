import functools
import datetime

def is_proper_date_time(func):
    """
    Decorator function for checking if the input is of proper function
    
    Syntax available:
        mamaya
        later
        soon
        maya
    """

    def _get_date_time_format(dt):
        """
        Returns the type of date-time the input is of.

        Type 1: Unknown Date in the near future
            'mamaya'
            'later'
            'soon'
            'maya'
        Type 2: Absolute Date

        Type 3: Relative Date

        """
        if dt.lower() in ['mamaya', 'later', 'soon', 'maya']:
            return 1
        else:
            raise ValueError

    @functools.wraps(func)
    def wrapper(reply):

        value = func(reply)
        msg = reply.content

        try:
            dt_format = _get_date_time_format(msg)
        except ValueError:
            print(f'Cannot strip "{msg}" into a date time object')
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(exception)
        
        if dt_format:
            return func(reply)

        return False
        
    return wrapper