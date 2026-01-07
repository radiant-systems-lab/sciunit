
from utcdatetime import utcdatetime
from datetime import datetime as _datetime
from email.utils import formatdate
import tzlocal
import time


now = utcdatetime.now
fromstring = utcdatetime.from_string


def localized(dt):
    return dt.astimezone(tzlocal.get_localzone())


def fmt_ls(dt):
    dt = localized(dt)
    return (dt.strftime('%b %-2d %H:%M')
            if dt.year == _datetime.today().year
            else dt.strftime('%b %-2d %-5Y'))


def fmt_iso(dt):
    dt = localized(dt)
    return dt.strftime('%Y-%m-%d %H:%M')


def fmt_rfc2822(dt):
    dt = localized(dt)
    return formatdate(time.mktime(dt.timetuple()), dt.tzinfo)
