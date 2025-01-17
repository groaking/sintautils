"""
sintautils
Created by: Samarthya Lykamanuella
Establishment year: 2025

LICENSE NOTICE:
===============

This file is part of sintautils.

sintautils is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

sintautils is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with sintautils. If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime as dt
from lxml import html
import requests as rq

from .exceptions import AuthorIDNotFoundException
from .exceptions import InvalidAuthorIDException
from .exceptions import InvalidLoginCredentialException
from .exceptions import InvalidParameterException
from .exceptions import MalformedDOMException
from .exceptions import NoLoginCredentialsException
from .exceptions import NonStringParameterException
from .backend import UtilBackEnd


class SintaScraper(object):
    """ The super-class for all SINTA scrapers in sintautils. Do not invoke directly! """

    # Determine the verbosity of loggings and debug messages.
    # Must be of: 0 (no verbose message), 1 (moderate logging level), and 2 (log all events)
    # If less than 0, it will be interpreted as 0.
    # If greater than 2, it will be interpreted as 2.
    verbosity = 1

    # Determine if the timestamp should be given in the logging message.
    log_timestamp = False

    def __init__(self, username: str = '', password: str = ''):
        self.username = username
        self.password = password

        # Initiating the session.
        self.s = rq.Session()

    def print(self, msg, verbose_level: int):
        """ Debug logging with verbosity control.
        :param msg: the message to be logged to the output terminal.
        :param verbose_level: between 0 and 2, determining on which verbosity level this message will be shown.
        """
        if self.verbosity < 0:
            self.verbosity = 0
        elif self.verbosity > 2:
            self.verbosity = 2

        # Do the message logging.
        if verbose_level <= self.verbosity:
            if self.log_timestamp:
                print('::: [' + str(dt.now()) + '] + ' + str(msg))
            else:
                print(str(msg))


class AV(SintaScraper):
    """ The scraper for the SINTA author verification site (https://sinta.kemdikbud.go.id/authorverification). """

    LOGIN_URL = 'https://sinta.kemdikbud.go.id/authorverification/login/do_login'

    URL_AUTHOR_SCOPUS = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=scopus'
    URL_AUTHOR_GSCHOLAR = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=google'

    def __init__(self, username: str = '', password: str = '', autologin: bool = False):
        if type(username) is not str or type(password) is not str:
            raise NonStringParameterException()

        elif username.strip() == '' or password.strip() == '':
            raise NoLoginCredentialsException()

        else:
            # We got the credential! Now let's proceed.
            super().__init__(username, password)

            if autologin:
                self.login()

    def _http_get_with_exception(self, url: str, author_id: str = ''):
        """ Send a GET HTTP request and throw errors in case of
        wrong credential or invalid input parameters, such as author_d. """

        r = self.s.get(url)
        if r.url == url:
            return r

        elif 'authorverification/login' in r.url:
            raise InvalidLoginCredentialException()

        elif 'authorverification/author/all' in r.url:
            raise AuthorIDNotFoundException(author_id)

    def _scrape_gscholar(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Google Scholar information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "author"
        - "journal"
        - "year"
        - "citations"
        - "url"
        """
        l = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not UtilBackEnd.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_GSCHOLAR.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="col-md-12"]/div[2]/div[2]/small/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())

        except IndexError:
            # This actually means that the author does not have a record. But still...
            self.print(f'Index error in attempting to read the pagination!', 2)
            page_to = 1

        # Preparing an empty list.
        s1, s2, s3, s4, s5, s6 = [], [], [], [], [], []

        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            self.print(f'Scraping page: {i}...', 2)

            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'

            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url, author_id=author_id)
            c = html.fromstring(r.text)

            # Title
            s1.extend([n.strip() for n in c.xpath(base + '//a/text()')])

            # Author
            s2.extend([n.replace('Author :', '').strip() for n in
                  c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')])

            # Journal name
            s3.extend([n.strip() for n in c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')])

            # Publication year
            s4.extend([n.strip() for n in c.xpath(base + '//td[2]//strong/text()')])

            # Citations
            s5.extend([n.strip() for n in c.xpath(base + '//td[3]//strong/text()')])

            # URL
            s6.extend([n.strip() for n in c.xpath(base + '//a/@href')])

        self.print(f'({len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)})', 2)

        if not len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6):
            raise MalformedDOMException(new_url)

        # Forge the Python dict.
        t = []
        for j in range(len(s1)):
            # Building the JSON dict.
            u = {}

            if '*' in fields or 'title' in fields:
                u['title'] = s1[j]

            if '*' in fields or 'author' in fields:
                u['author'] = s2[j]

            if '*' in fields or 'journal' in fields:
                u['journal'] = s3[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s4[j]

            if '*' in fields or 'citations' in fields:
                u['citations'] = s5[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s6[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'author' in fields:
            d['author'] = s2

        if '*' in fields or 'journal' in fields:
            d['journal'] = s3

        if '*' in fields or 'year' in fields:
            d['year'] = s4

        if '*' in fields or 'citations' in fields:
            d['citations'] = s5

        if '*' in fields or 'url' in fields:
            d['url'] = s6

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d

    def _scrape_scopus(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Scopus information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "name"
        - "creator"
        - "journal"
        - "type"
        - "year"
        - "citations"
        - "quartile"
        - "url"
        """
        l = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not UtilBackEnd.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_SCOPUS.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id =author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="col-md-12"]/div[2]/div[2]/small/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int( s[1].strip() )

        except IndexError:
            # This actually means that the author does not have a record. But still...
            self.print(f'Index error in attempting to read the pagination!', 2)
            page_to = 1

        # Preparing an empty list.
        s1, s2, s3, s4, s5, s6, s7, s8 = [], [], [], [], [], [], [], []

        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            self.print(f'Scraping page: {i}...', 2)

            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'

            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url, author_id=author_id)
            c = html.fromstring(r.text)

            # Name
            s1.extend([n.strip() for n in c.xpath(base + '//a/text()')])

            # Creator
            s2.extend([n.replace('Creator :', '').strip() for n in
                  c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')])

            # Journal name
            s3.extend([n.strip() for n in c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')])

            # Publication type
            s4.extend([n.strip() for n in c.xpath(base + '//td[3]//strong[1]/text()')])

            # Publication year
            s5.extend([n.strip() for n in c.xpath(base + '//td[3]//strong[2]/text()')])

            # Citations
            s6.extend([n.strip() for n in c.xpath(base + '//td[4]//strong/text()')])

            # Quartile
            s7.extend([n.strip() for n in c.xpath(base + '//td[1]/div/text()')])

            # URL
            s8.extend([n.strip() for n in c.xpath(base + '//a/@href')])

        self.print(f'({len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}, {len(s7)}, {len(s8)})', 2)

        if not len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6) == len(s7) == len(s8):
            raise MalformedDOMException(new_url)

        # Forge the Python dict.
        t = []
        for j in range(len(s1)):
            # Building the JSON dict.
            u = {}

            if '*' in fields or 'name' in fields:
                u['name'] = s1[j]

            if '*' in fields or 'creator' in fields:
                u['creator'] = s2[j]

            if '*' in fields or 'journal' in fields:
                u['journal'] = s3[j]

            if '*' in fields or 'type' in fields:
                u['type'] = s4[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s5[j]

            if '*' in fields or 'citations' in fields:
                u['citations'] = s6[j]

            if '*' in fields or 'quartile' in fields:
                u['quartile'] = s7[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s8[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'name' in fields:
            d['name'] = s1

        if '*' in fields or 'creator' in fields:
            d['creator'] = s2

        if '*' in fields or 'journal' in fields:
            d['journal'] = s3

        if '*' in fields or 'type' in fields:
            d['type'] = s4

        if '*' in fields or 'year' in fields:
            d['year'] = s5

        if '*' in fields or 'citations' in fields:
            d['citations'] = s6

        if '*' in fields or 'quartile' in fields:
            d['quartile'] = s7

        if '*' in fields or 'url' in fields:
            d['url'] = s8

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d

    def get_gscholar(self, author_id: list = [], out_format: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's Google Scholar data.

        :param author_id: the list of author IDs to be scraped.
        :param out_format: the format of the output result document.

        Currently, the only supported formats are as follows:
        - "csv"
        - "json"

        You can only specify one output format at a time.

        :param fields: the types of field to be scraped.

        Currently, the only supported fields are as follows:
        - "*"
        - "title"
        - "author"
        - "journal"
        - "year"
        - "citations"
        - "url"

        You can input more than one field. For instance:
        - ["journal", "url"]
        - ["title", "author", "year"]

        Use asterisk in order to return all fields:
        - ["*"]
        """

        if type(author_id) is str:
            a = self._scrape_gscholar(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for author ID: {l}...', 2)
                a.extend(self._scrape_gscholar(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    def get_scopus(self, author_id: list = [], out_format: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's scopus data.

        :param author_id: the list of author IDs to be scraped.
        :param out_format: the format of the output result document.
        
        Currently, the only supported formats are as follows:
        - "csv"
        - "json"
        
        You can only specify one output format at a time.
        
        :param fields: the types of field to be scraped.
        
        Currently, the only supported fields are as follows:
        - "*"
        - "name"
        - "creator"
        - "journal"
        - "type"
        - "year"
        - "citations"
        - "quartile"
        - "url"
        
        You can input more than one field. For instance:
        - ["journal", "url"]
        - ["quartile", "citations", "year"]

        Use asterisk in order to return all fields:
        - ["*"]
        """

        if type(author_id) is str:
            a = self._scrape_scopus(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for creator ID: {l}...', 2)
                a.extend(self._scrape_scopus(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    def login(self):
        """ Performs the credential login and obtains the session cookie for this account. """
        r = self.s.post(self.LOGIN_URL, data = {'username': self.username, 'password': self.password})
        self.print(r.status_code, 2)
        self.print(r.url, 2)

        if 'dashboard' in r.url:
            self.print('Login successful!', 1)
        else:
            raise InvalidLoginCredentialException()
