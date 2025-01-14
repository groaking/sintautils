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

from .exceptions import AuthorIDNotFoundException
from .exceptions import InvalidAuthorIDException
from .exceptions import InvalidLoginCredentialException
from .exceptions import NoLoginCredentialsException
from .exceptions import NonStringParameterException


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
    
    def print(self, msg: str, verbose_level: int):
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
    
    def _validate_author_id(self, n):
        """ Return true if the input parameter is a valid ID, false if it contains illegal characters. """
        
        try:
            int(str(n))
            return True
            
        except ValueError:
            return False
        
        return False
    
    def __init__(self, username: str = '', password: str = '', autologin: bool = False):
        if type(username) != str or type(password) != str:
            raise NonStringParameterException()
        
        elif username.strip() == '' or password.strip() == '':
            raise NoLoginCredentialsException()
        
        else:
            # We got the credential! Now let's proceed.
            super().__init__(username, password)
            
            if autologin:
                self.login()
    
    def get_scopus(self, author_id: list = [], output: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's scopus data.
        
        :param id_list: the list of author IDs to be scraped.
        :param output: the format of the output result document.
        
        Currently, the only supported formats are as follows:
        - "csv"
        - "json"
        - "xlsx"
        
        You can only specify one output format at a time.
        
        :param fields: the types of field to be scraped.
        
        Currently, the only supported fields are as follows:
        - "*"
        - "title"
        - "creator"
        - "document_type"
        - "publish_year"
        - "publication"
        - "citations"
        - "quartile"
        
        You can input more than one field. For instance:
        - "title creator"
        - "title,document_type,citations"
        """
        
        if type(author_id) != str:
            pass
            # TODO:
            # Directly scrape this singluar string.
        
        for l in author_id:
            l = str(l).strip()
            
            # Validating the author ID.
            if self._validate_author_id(l) == False:
                raise InvalidAuthorIDException()
            
            # Try to open the author's specific menu page.
            url = self.URL_AUTHOR_SCOPUS.replace('%%%', l)
            r = self.s.get(url)
            
            if r.url == url:
                self.print('Begin scrapping author ID ' + l + '...', 1)
            
            elif 'authorverification/login' in r.url:
                raise InvalidLoginCredentialException()
            
            elif 'authorverification/author/all' in r.url:
                raise AuthorIDNotFoundException(l)
    
    def login(self):
        """ Performs the credential login and obtains the session cookie for this account. """
        r = self.s.post(self.LOGIN_URL, data = {'username': self.username, 'password': self.password})
        self.print(r.status_code, 2)
        self.print(r.url, 2)
        
        if 'dashboard' in r.url:
            self.print('Login successful!', 1)
        else:
            raise InvalidLoginCredentialException()
        