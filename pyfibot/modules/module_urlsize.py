"""
Warns about large files

$Id$
$HeadURL$
"""
from __future__ import unicode_literals, print_function, division
import requests


def handle_url(bot, user, channel, url, msg):
    """inform about large files (over 5MB)"""

    # TODO: Use reference from bot / config
    browser = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11"

    s = requests.session()
    s.stream = True  # Don't fetch content unless asked
    s.headers.update({'User-Agent':browser})
    r = s.get(url)

    size = int(r.headers.get('Content-Length', 0))
    content_type = r.headers.get('content-type', None)
    if not content_type:
        content_type = "Unknown"
    size = size / 1024 / 1024

    # report files over 5 MB
    if size > 5:
        return bot.say(channel, "File size: %s MB - Content-Type: %s" % (int(size), content_type))
