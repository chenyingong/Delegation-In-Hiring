import datetime


def last_day(today: datetime.date, n: int) -> datetime.date:
    """
    Return the last day of the month n months before today.
    :param today: date of today
    :param n: the number of months before today
    :return: the last day of the month n months before today
    """
    if n <= 0:
        raise ValueError("n must be bigger than 0")
    first = datetime.date(today.year, today.month, 1)
    last = datetime.date.max
    while n > 0:
        # the last day of the last month
        last = first - datetime.timedelta(days=1)
        # the first day of the last month
        first = datetime.date(last.year, last.month, 1)
        n -= 1
    return last


def first_day(today: datetime.date, n: int) -> datetime.date:
    """
    Return the first day of the month n months before today.
    :param today: date of today
    :param n: the number of months before today
    :return: the first day of the month n months before today
    """
    if n <= 0:
        raise ValueError("n must be bigger than 0")
    # the last day of the month n months before today
    last = last_day(today, n)
    first = datetime.date(last.year, last.month, 1)
    return first


def to_date(date) -> str:
    """
    Convert data-time type to string.

    :param date: datetime object
    :return: string representation of the date
    """
    if date == '-':
        return '-'
    elif isinstance(date, str):
        return date
    else:
        return str(date.date())


def month_delta(start_date: str, end_date: str):
    """
    Return the month difference of end_date and start_date
        :param start_date: start date
        :param end_date: end date
        :return:  the month difference of the end_date and the start date
    """
    if (start_date == '-') or (end_date == '-'):
        return  # return null to guarantee that sort algorithm could work
    date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()  # str to date
    date2 = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    flag = True
    if date1 > date2:
        date1, date2 = date2, date1
        flag = False
    year_diff = date2.year - date1.year
    end_month = year_diff * 12 + date2.month
    delta = end_month - date1.month
    return -delta if flag is False else delta


def same_month(this_date: str, that_date: str) -> bool:
    """
    Is this_date on the same month as that_date?

    :param this_date: this date
    :param that_date: that date
    :return: true if on the same month, false otherwise 
    """
    # convert str obj to date obj
    this = datetime.datetime.strptime(this_date, '%Y-%m-%d').date()
    that = datetime.datetime.strptime(that_date, '%Y-%m-%d').date()
    this_year = this.year
    that_year = that.year
    this_month = this.month
    that_month = that.month
    if (this_month == that_month) and (this_year == that_year):
        return True
    else:
        return False

def peer_group(date_string: str) -> int:
    """
    Return the peer group the date belonging to.
    :param date_string: string format of the date
    :return: the peer group the date belonging to
    """
    if date_string == '-':
        return 0
    current = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()  # str to date type
    today = datetime.date.today()
    if current >= first_day(today, 3):
        return 1
    elif last_day(today, 4) >= current >= first_day(today, 6):
        return 2
    elif last_day(today, 7) >= current >= first_day(today, 12):
        return 3
    elif last_day(today, 13) >= current:
        return 4


def is_senior(date_string: str) -> bool:
    """
    Return True if the date is belonging to senior group, False otherwise.
    :param date_string: string format of the date
    :return: True if the date is belonging to senior group, False otherwise
    """
    if date_string == '-':  # nan has already been converted to '-'
        return False  # keep the unknown date because of the analysis requirement of the experiment
    current = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()  # str转date
    today = datetime.date.today()
    if last_day(today, 13) >= current >= datetime.date(2017, 12, 1):
        return True
    else:
        return False
