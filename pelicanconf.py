#!/usr/bin/env python3

from datetime import datetime

AUTHOR = "Emiel van de Laar"
SITENAME = "Galloping Alligator"
SITESUBTITLE = "My thoughts on tech and other things..."
SITEURL = ""

PATH = "content"

TIMEZONE = "Europe/Amsterdam"

DEFAULT_DATE_FORMAT = "%d %b %Y"

DEFAULT_LANG = "en"

SUMMARY_MAX_LENGTH = 42

# Feed generation is usually not desired when developing
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
CATEGORY_FEED_ATOM = None
FEED_ALL_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = []

# Social links
SOCIAL = [
    ("GitHub", "https://github.com/emiel"),
    ("Mastodon", "https://hachyderm.io/@emiel"),
    ("e-mail", "mailto:gemiel@gmail.com"),
]

DEFAULT_PAGINATION = False

STATIC_PATHS = [
    "extra/CNAME",
    "extra/robots.txt",
]

EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/robots.txt": {"path": "robots.txt"},
}

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = "themes/mineral"

# Pelican theme settings

# SITESUBTITLE = ''
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False

# ABOUT_PAGE = '/pages/about.html'

COPYRIGHT_YEAR = f"2014&ndash;{datetime.now().year}"
