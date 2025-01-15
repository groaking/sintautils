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
import json
import requests as rq

from .exceptions import AuthorIDNotFoundException
from .exceptions import InvalidAuthorIDException
from .exceptions import InvalidLoginCredentialException
from .exceptions import InvalidParameterException
from .exceptions import MalformedDOMException
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
    
    def _json_to_table(self, data):
        """ Convert Python dict or list into table.
        :returns: A pandas DataFrame object.
        """
    
    def _http_get_with_exception(self, url: str):
        """ Send a GET HTTP request and throw errors in case of
        wrong credential or invalid input parameters. """
        
        r = self.s.get(url)
        if r.url == url:
            return r
        
        elif 'authorverification/login' in r.url:
            raise InvalidLoginCredentialException()
        
        elif 'authorverification/author/all' in r.url:
            raise AuthorIDNotFoundException(l)
    
    def _scrape_scopus(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Scopus information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.
        
        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)
        
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
        """
        l = str(author_id).strip()
        
        # Validating the output format.
        if not out_format in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')
            
        # Validating the author ID.
        if self._validate_author_id(l) == False:
            raise InvalidAuthorIDException()
        
        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_SCOPUS.replace('%%%', l)
        r = self._http_get_with_exception(url)
        
        self.print('Begin scrapping author ID ' + l + '...', 2)
        
        # Get the list of pagination.
        c = html.fromstring(r.text)
        s = c.xpath('//*[@class="col-md-6 text-center text-lg-left light-font  mb-3"]/small/text()')[0]
        s = s.split('|')[0].replace('Page', '').split('of')
        page_from = int( s[0].replace('Page', '').strip() )
        page_to = int( s[1].strip() )
        
        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            
            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'
            
            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url)
            c = html.fromstring(r.text)
            
            # Name
            try:
                s1 = [n.strip() for n in c.xpath(base + '//a/text()')]
            except:
                s1 = []
            
            # Creator
            try:
                s2 = [n.replace('Creator :', '').strip() for n in c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')]
            except:
                s2 = []
            
            # Journal name
            try:
                s3 = [n.strip() for n in c.xpath(base + '//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')]
            except:
                s3 = []
            
            # Publication type
            try:
                s4 = [n.strip() for n in c.xpath(base + '//td[3]//strong[1]/text()')]
            except:
                s4 = []
            
            # Publication year
            try:
                s5 = [n.strip() for n in c.xpath(base + '//td[3]//strong[2]/text()')]
            except:
                s5 = []
            
            # Citations
            try:
                s6 = [n.strip() for n in c.xpath(base + '//td[4]//strong/text()')]
            except:
                s6 = []
            
            # Quartile
            try:
                s7 = [n.strip() for n in c.xpath(base + '//td[1]/div/text()')]
            except:
                s7 = []
            
            # URL
            try:
                s8 = [n.strip() for n in c.xpath(base + '//a/@href')]
            except:
                s8 = []
            
            self.print(f'{len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}, {len(s7)}, {len(s8)})', 2)
            
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
            d = {
                'name': s1,
                'creator': s2,
                'journal': s3,
                'type': s4,
                'year': s5,
                'citations': s6,
                'quartile': s7,
                'url': s8,
            }
            
            if out_format == 'json':
                return t
            elif out_format == 'csv':
                return d
    
    def get_scopus(self, author_id: list = [], out: str = '', out_format: str = 'csv', fields: list = ['*']):
        """ Performs the scraping of individual author's scopus data.
        
        :param id_list: the list of author IDs to be scraped.
        :param out_format: the format of the output result document.
        
        Currently, the only supported formats are as follows:
        - "csv"
        - "json"
        - "xlsx"
        
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
        """
        
        if type(author_id) == str:
            a = self._scrape_scopus(author_id = author_id, out_format = "csv", fields = fields)
        
        elif type(author_id) == list:
            a = []
            for l in author_id:
                a.extend(self._scrape_scopus(author_id = l, out_format = "csv", fields = fields))
            
        else:
            raise InvalidParameterException('You can only pass list or string into this function')
        
        if out.strip() == '':
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
        