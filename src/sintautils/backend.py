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
from lxml import html
from requests import Session

from .exceptions import InvalidParameterException, InvalidAuthorIDException, \
    InvalidLoginCredentialException, AuthorIDNotFoundException, MalformedDOMException


class UtilBackEnd(object):
    """ The back-end of sintautils that contain static functions and methods. """

    URL_AUTHOR_SCOPUS = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=scopus'
    URL_AUTHOR_WOS = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=wos'
    URL_AUTHOR_GSCHOLAR = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=google'

    def __init__(self, requests_session: Session, logger: ()):
        super().__init__()
        self.print = logger
        self.s = requests_session

    @staticmethod
    def validate_author_id(n):
        """ Return true if the input parameter is a valid ID, false if it contains illegal characters. """

        try:
            int(str(n))
            return True

        except ValueError:
            return False

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

    # noinspection PyDefaultArgument
    def scrape_gscholar(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
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
        l: str = str(author_id).strip()

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

        # Preparing the temporary URL.
        new_url: str = str()

        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            self.print(f'Scraping page: {i}...', 2)

            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url, author_id=author_id)
            c = html.fromstring(r.text)

            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Author.
                try:
                    x: str = a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')[0]
                    if x.__contains__('Author :'):
                        s2.append(x.replace('Author :', '').strip())
                    else:
                        # This is publication info, not author info.
                        # The author info must be missing.
                        s2.append('')
                except IndexError:
                    s2.append('')

                # Journal name.
                try:
                    s3.append(a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')[0].strip())
                except IndexError:
                    s3.append('')

                # Publication year.
                try:
                    s4.append(a.xpath('.//td[2]//strong/text()')[0].strip())
                except IndexError:
                    s4.append('')

                # Citations.
                try:
                    s5.append(a.xpath('.//td[3]//strong/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # URL.
                try:
                    s6.append(a.xpath('.//a/@href')[0].strip())
                except IndexError:
                    s6.append('')

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

    # noinspection PyDefaultArgument
    def scrape_scopus(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Scopus information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "author"
        - "journal"
        - "type"
        - "year"
        - "citations"
        - "quartile"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not UtilBackEnd.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_SCOPUS.replace('%%%', l)
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
        s1, s2, s3, s4, s5, s6, s7, s8 = [], [], [], [], [], [], [], []

        # Preparing the temporary URL.
        new_url: str = str()

        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            self.print(f'Scraping page: {i}...', 2)

            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url, author_id=author_id)
            c = html.fromstring(r.text)

            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Author.
                try:
                    x: str = a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')[0]
                    if x.__contains__('Creator :'):
                        s2.append(x.replace('Creator :', '').strip())
                    else:
                        # This is publication info, not author info.
                        # The author info must be missing.
                        s2.append('')
                except IndexError:
                    s2.append('')

                # Journal name.
                try:
                    s3.append(a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')[0].strip())
                except IndexError:
                    s3.append('')

                # Publication type.
                try:
                    s4.append(a.xpath('.//td[3]//strong[1]/text()')[0].strip())
                except IndexError:
                    s4.append('')

                # Publication year.
                try:
                    s5.append(a.xpath('.//td[3]//strong[2]/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # Citations.
                try:
                    s6.append(a.xpath('.//td[4]//strong/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Quartile.
                try:
                    s7.append(a.xpath('.//td[1]/div/text()')[0].strip())
                except IndexError:
                    s7.append('')

                # URL.
                try:
                    s8.append(a.xpath('.//a/@href')[0].strip())
                except IndexError:
                    s8.append('')

        self.print(f'({len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}, {len(s7)}, {len(s8)})', 2)

        if not len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6) == len(s7) == len(s8):
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
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'author' in fields:
            d['author'] = s2

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

    # noinspection PyDefaultArgument
    def scrape_wos(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Web of Science (WOS) information of one, and only one author in SINTA.
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
        - "quartile"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not UtilBackEnd.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_WOS.replace('%%%', l)
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
        s1, s2, s3, s4, s5, s6, s7 = [], [], [], [], [], [], []

        # Preparing the temporary URL.
        new_url: str = str()

        # Begin the scraping.
        i = 0
        while i < page_to:
            i += 1
            self.print(f'Scraping page: {i}...', 2)

            # Opens the URL of this page.
            new_url = url + '&page=' + str(i)
            r = self._http_get_with_exception(new_url, author_id=author_id)
            c = html.fromstring(r.text)

            # The base tag.
            base = '//div[@class="table-responsive"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Author.
                try:
                    x: str = a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[1]/text()')[0]
                    if x.__contains__('Authors :'):
                        s2.append(x.replace('Authors :', '').strip())
                    else:
                        # This is publication info, not author info.
                        # The author info must be missing.
                        s2.append('')
                except IndexError:
                    s2.append('')

                # Journal name.
                try:
                    s3.append(a.xpath('.//td[@class="text-lg-nowrap text-nowrap"]//small[2]/text()')[0].strip())
                except IndexError:
                    s3.append('')

                # Publication year.
                try:
                    s4.append(a.xpath('.//td[3]//strong/text()')[0].strip()[-4:])
                except IndexError:
                    s4.append('')

                # Citations.
                try:
                    s5.append(a.xpath('.//td[4]//strong/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # Quartile.
                try:
                    s6.append(a.xpath('.//td[1]/div/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # URL.
                try:
                    s7.append(a.xpath('.//a/@href')[0].strip())
                except IndexError:
                    s7.append('')

        self.print(f'({len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}, {len(s7)})', 2)

        if not len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6) == len(s7):
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

            if '*' in fields or 'quartile' in fields:
                u['quartile'] = s6[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s7[j]

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

        if '*' in fields or 'quartile' in fields:
            d['quartile'] = s6

        if '*' in fields or 'url' in fields:
            d['url'] = s7

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d
