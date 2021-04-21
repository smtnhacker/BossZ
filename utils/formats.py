import functools
from datetime import datetime
from dateutil import tz, parser
from dateutil.relativedelta import relativedelta
import dateparser

def get_date_time_format(dt):
    """
    Returns the type of date-time the input is of.

    Parameter
    -------------
    dt : string
        The deltatime required
    
    Return
    ------------
    res : datetime object
        The date in the future representing the delta-time

    """

    now = datetime.now(tz=tz.tzlocal())
    new_date = None

    # Try absolute date first
    try:
        new_date = parser.parse(dt)
    except ValueError as e:
        exception = f"{type(e).__name__}: {e}"
        print(exception)
    except Exception as e:
        exception = f"{type(e).__name__}:"
        print(exception)
        return None
    else:
        new_date = new_date.replace(tzinfo=tz.tzlocal())
        print(f'Obtained the absolute date: {new_date} from {dt}')

    if new_date:
        return new_date

    # Try known relative date second
    try:
        new_date = dateparser.parse(dt)
        if not new_date:
            raise ValueError(f'ParserError: dateparser cannot parse {dt}')
    except ValueError as e:
        exception = f"{type(e).__name__}: {e}"
        print(exception)
    except Exception as e:
        exception = f"{type(e).__name__}: {e}"
        print(exception)
        return None
    else:
        new_date = new_date.replace(tzinfo=tz.tzlocal())
        print(f'Obtained the relative date: {new_date} from {dt}')

    if new_date:
        return new_date
    
    # Try slang date third
    if dt.lower() in ['kahapon', 'yesterday']:
        new_date = now + relativedelta(days=-1)
    elif dt.lower() in ['kanina', 'awhile ago']:
        new_date = now + relativedelta(hours=-2)
    elif dt.lower() in ['mamaya', 'maya', 'laters', 'tsaka na', 'later', 'basta', 'soon']:
        new_date = now + relativedelta(hours=2)
    elif dt.lower() in ['bukas', 'tom', 'tomorrow']:
        new_date = now + relativedelta(days=1)
    
    return new_date

def is_proper_date_time(func):
    """
    Decorator function for checking if the input is of proper function
    """

    @functools.wraps(func)
    def wrapper(reply):

        value = func(reply)
        msg = reply.content

        try:
            dt_format = get_date_time_format(msg)
        except ValueError:
            print(f'Cannot strip "{msg}" into a date time object')
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(exception)
        
        if dt_format:
            return func(reply)

        return False
        
    return wrapper

if __name__ == '__main__':

    TEST_DATES = [
        'mamaya',
        'bukas',
        'August 5 2020',
        'tomorrow',
        'later',
        'in 2 weeks',
        'in 3 days'
    ]
    print(datetime.now(tz=tz.tzlocal()))

    for dt in TEST_DATES:
        print(f'Attempting to parse {dt}')
        print(datetime.now(tz=tz.tzlocal()) <= get_date_time_format(dt))
        print(f'{dt} -> {get_date_time_format(dt)}', end='\n\n')