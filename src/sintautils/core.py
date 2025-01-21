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
import requests as rq

from .exceptions import InvalidLoginCredentialException
from .exceptions import InvalidParameterException
from .exceptions import NoLoginCredentialsException
from .exceptions import NonStringParameterException
from .backend import UtilBackEnd


# noinspection SpellCheckingInspection
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

    def __init__(self, username: str = '', password: str = '', autologin: bool = False):
        if type(username) is not str or type(password) is not str:
            raise NonStringParameterException()

        elif username.strip() == '' or password.strip() == '':
            raise NoLoginCredentialsException()

        else:
            # We got the credential! Now let's proceed.
            super().__init__(username, password)

            # Initializing the back-end.
            self.backend = UtilBackEnd(self.s, self.print)

            if autologin:
                self.login()

    # noinspection PyDefaultArgument
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
            a = self.backend.scrape_gscholar(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for author ID: {l}...', 2)
                a.extend(self.backend.scrape_gscholar(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    # noinspection PyDefaultArgument
    def get_ipr(self, author_id: list = [], out_format: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's IPR data.

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
        - "application_no"
        - "inventor"
        - "patent_holder"
        - "category"
        - "year"
        - "status"

        You can input more than one field. For instance:
        - ["inventor", "status"]
        - ["title", "patent_holder", "status"]

        Use asterisk in order to return all fields:
        - ["*"]
        """

        if type(author_id) is str:
            a = self.backend.scrape_ipr(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for author ID: {l}...', 2)
                a.extend(self.backend.scrape_ipr(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    # noinspection PyDefaultArgument
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
        - "title"
        - "author"
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
            a = self.backend.scrape_scopus(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for author ID: {l}...', 2)
                a.extend(self.backend.scrape_scopus(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    # noinspection PyDefaultArgument
    def get_wos(self, author_id: list = [], out_format: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's Web of Science (WOS) data.

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
        - "quartile"
        - "url"

        You can input more than one field. For instance:
        - ["journal", "url"]
        - ["quartile", "citations", "year"]

        Use asterisk in order to return all fields:
        - ["*"]
        """

        if type(author_id) is str:
            a = self.backend.scrape_wos(author_id=str(author_id), out_format=out_format, fields=fields)

        elif type(author_id) is list:
            a = []
            for l in author_id:
                self.print(f'Scraping for author ID: {l}...', 2)
                a.extend(self.backend.scrape_wos(author_id=l, out_format=out_format, fields=fields))

        else:
            raise InvalidParameterException('You can only pass list or string into this function')

        return a

    def login(self):
        """ Performs the credential login and obtains the session cookie for this account. """
        r = self.s.post(self.LOGIN_URL, data={'username': self.username, 'password': self.password})
        self.print(r.status_code, 2)
        self.print(r.url, 2)

        if 'dashboard' in r.url:
            self.print('Login successful!', 1)
        else:
            raise InvalidLoginCredentialException()
