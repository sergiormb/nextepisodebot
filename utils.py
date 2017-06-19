import re

from pytz import timezone
from dateutil import parser


def remove_tag(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


def convert_to_timezone(date_time):
    return date_time.astimezone(timezone('Europe/Madrid'))


def convert_to_datetime(date):
    return parser.parse(date)
