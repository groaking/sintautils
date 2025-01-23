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

    URL_AUTHOR_BOOK = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=book'
    URL_AUTHOR_GARUDA = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=garuda'
    URL_AUTHOR_GSCHOLAR = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=google'
    URL_AUTHOR_IPR = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=ipr'
    URL_AUTHOR_SCOPUS = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=scopus'
    URL_AUTHOR_RESEARCH = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=research'
    URL_AUTHOR_SERVICE = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=service'
    URL_AUTHOR_WOS = 'https://sinta.kemdikbud.go.id/authorverification/author/profile/%%%?view=wos'

    def __init__(self, requests_session: Session, logger: ()):
        super().__init__()
        self.print = logger
        self.s = requests_session

    @staticmethod
    def _book_heuristics_handler(el):
        """ Scrape with validation a given book row's ISBN, author, publisher, and page information.

        :param el: the XPATH element as DOM object to consider for element detection.
        :return: a dict of the following keys: "isbn", "author", "publisher", and "page".
        """
        ret_dict: dict = {}

        # Scraping each <small> element.
        try:
            s1 = el.xpath('./small[1]/text()')[0]
        except IndexError:
            s1 = ''
        try:
            s2 = el.xpath('./small[2]/text()')[0]
        except IndexError:
            s2 = ''
        try:
            s3 = el.xpath('./small[3]/text()')[0]
        except IndexError:
            s3 = ''
        try:
            s4 = el.xpath('./small[4]/text()')[0]
        except IndexError:
            s4 = ''

        # Carry out the heuristics.
        a = ['ISBN : ', 'Author : ']
        b = ['isbn', 'author']
        for i in range(len(a)):
            lookup_word = a[i]
            key = b[i]
            if s1.__contains__(lookup_word):
                ret_dict[key] = s1.replace(lookup_word, '')
            elif s2.__contains__(lookup_word):
                ret_dict[key] = s2.replace(lookup_word, '')
            elif s3.__contains__(lookup_word):
                ret_dict[key] = s3.replace(lookup_word, '')
            elif s4.__contains__(lookup_word):
                ret_dict[key] = s4.replace(lookup_word, '')
            else:
                ret_dict[key] = ''

        # Now for the special case.
        if s1.__contains__('|'):
            x = s1.split('|')
            ret_dict['publisher'] = x[0].strip()
            ret_dict['page'] = x[1].replace('Page', '').strip()
        elif s2.__contains__('|'):
            x = s2.split('|')
            ret_dict['publisher'] = x[0].strip()
            ret_dict['page'] = x[1].replace('Page', '').strip()
        elif s3.__contains__('|'):
            x = s3.split('|')
            ret_dict['publisher'] = x[0].strip()
            ret_dict['page'] = x[1].replace('Page', '').strip()
        elif s4.__contains__('|'):
            x = s4.split('|')
            ret_dict['publisher'] = x[0].strip()
            ret_dict['page'] = x[1].replace('Page', '').strip()
        else:
            ret_dict['publisher'] = ''
            ret_dict['page'] = ''

        return ret_dict

    @staticmethod
    def _garuda_heuristics_handler(el):
        """ Determines whether a given DOM element contains parameters existing in the "Garuda" data.

        :param el: the XPATH element as DOM object to consider for element detection.
        :return: a dict of the following keys: "publisher", "author", "journal", and "doi".
        """
        ret_dict: dict = {}

        # Scraping each <small> element.
        try:
            s1 = el.xpath('./small[1]/text()')[0]
        except IndexError:
            s1 = ''
        try:
            s2 = el.xpath('./small[2]/text()')[0]
        except IndexError:
            s2 = ''
        try:
            s3 = el.xpath('./small[3]/text()')[0]
        except IndexError:
            s3 = ''
        try:
            s4 = el.xpath('./small[4]/text()')[0]
        except IndexError:
            s4 = ''

        # Carry out the heuristics.
        a = ['DOI: ']
        b = ['doi']
        for i in range(len(a)):
            lookup_word = a[i]
            key = b[i]
            if s1.__contains__(lookup_word):
                ret_dict[key] = s1.replace(lookup_word, '')
            elif s2.__contains__(lookup_word):
                ret_dict[key] = s2.replace(lookup_word, '')
            elif s3.__contains__(lookup_word):
                ret_dict[key] = s3.replace(lookup_word, '')
            elif s4.__contains__(lookup_word):
                ret_dict[key] = s4.replace(lookup_word, '')
            else:
                ret_dict[key] = ''

        # Special cases.
        ret_dict['publisher'] = s1
        ret_dict['author'] = s2
        ret_dict['journal'] = s3

        return ret_dict

    @staticmethod
    def _ipr_heuristics_handler(el):
        """ Determines whether a given DOM element contains "No. Permohonan", "Inventor", or "Pemegang Paten" strings.

        :param el: the XPATH element as DOM object to consider for element detection.
        :return: a dict of the following keys: "application_no", "inventor", and "patent_holder".
        """
        ret_dict: dict = {}

        # Scraping each <small> element.
        try:
            s1 = el.xpath('./small[@class="text-muted"][1]/text()')[0]
        except IndexError:
            s1 = ''
        try:
            s2 = el.xpath('./small[@class="text-muted"][2]/text()')[0]
        except IndexError:
            s2 = ''
        try:
            s3 = el.xpath('./small[@class="text-muted"][3]/text()')[0]
        except IndexError:
            s3 = ''

        # Carry out the heuristics.
        a = ['No. Permohonan : ', 'Inventor : ', 'Pemegang Paten : ']
        b = ['application_no', 'inventor', 'patent_holder']
        for i in range(len(a)):
            lookup_word = a[i]
            key = b[i]
            if s1.__contains__(lookup_word):
                ret_dict[key] = s1.replace(lookup_word, '')
            elif s2.__contains__(lookup_word):
                ret_dict[key] = s2.replace(lookup_word, '')
            elif s3.__contains__(lookup_word):
                ret_dict[key] = s3.replace(lookup_word, '')
            else:
                ret_dict[key] = ''

        return ret_dict

    @staticmethod
    def _research_heuristics_handler(el):
        """ Determines whether a given DOM element contains "Funds approved", "Program Hibah", or "Skema" strings.

        :param el: the XPATH element as DOM object to consider for element detection.
        :return: a dict of the following keys: "funds", "program", and "schema".
        """
        ret_dict: dict = {}

        # Scraping each <small> element.
        try:
            s1 = el.xpath('./small[1]/text()')[0]
        except IndexError:
            s1 = ''
        try:
            s2 = el.xpath('./small[2]/text()')[0]
        except IndexError:
            s2 = ''
        try:
            s3 = el.xpath('./small[3]/text()')[0]
        except IndexError:
            s3 = ''
        try:
            s4 = el.xpath('./small[4]/text()')[0]
        except IndexError:
            s4 = ''

        # Carry out the heuristics.
        a = ['Funds approved : ', 'Program Hibah : ', 'Skema : ']
        b = ['funds', 'program', 'schema']
        for i in range(len(a)):
            lookup_word = a[i]
            key = b[i]
            if s1.__contains__(lookup_word):
                ret_dict[key] = s1.replace(lookup_word, '')
            elif s2.__contains__(lookup_word):
                ret_dict[key] = s2.replace(lookup_word, '')
            elif s3.__contains__(lookup_word):
                ret_dict[key] = s3.replace(lookup_word, '')
            elif s4.__contains__(lookup_word):
                ret_dict[key] = s4.replace(lookup_word, '')
            else:
                ret_dict[key] = ''

        return ret_dict

    @staticmethod
    def _service_heuristics_handler(el):
        """ Determines whether a given DOM element contains "Funds approved", "Program Hibah", or "Skema" strings.

        :param el: the XPATH element as DOM object to consider for element detection.
        :return: a dict of the following keys: "funds", "program", and "schema".
        """
        ret_dict: dict = {}

        # Scraping each <small> element.
        try:
            s1 = el.xpath('./small[1]/text()')[0]
        except IndexError:
            s1 = ''
        try:
            s2 = el.xpath('./small[2]/text()')[0]
        except IndexError:
            s2 = ''
        try:
            s3 = el.xpath('./small[3]/text()')[0]
        except IndexError:
            s3 = ''
        try:
            s4 = el.xpath('./small[4]/text()')[0]
        except IndexError:
            s4 = ''

        # Carry out the heuristics.
        a = ['Funds approved : ', 'Program Hibah : ', 'Skema : ']
        b = ['funds', 'program', 'schema']
        for i in range(len(a)):
            lookup_word = a[i]
            key = b[i]
            if s1.__contains__(lookup_word):
                ret_dict[key] = s1.replace(lookup_word, '')
            elif s2.__contains__(lookup_word):
                ret_dict[key] = s2.replace(lookup_word, '')
            elif s3.__contains__(lookup_word):
                ret_dict[key] = s3.replace(lookup_word, '')
            elif s4.__contains__(lookup_word):
                ret_dict[key] = s4.replace(lookup_word, '')
            else:
                ret_dict[key] = ''

        return ret_dict

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
    def scrape_book(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the book information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "isbn"
        - "author"
        - "publisher"
        - "page"
        - "year"
        - "location"
        - "thumbnail"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not self.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_BOOK.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="row"]/div[@class="col-6 text-right"]/small/i/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())
            self.print('Detected number of pages: ' + str(page_to), 2)

        except IndexError:
            # This actually means that the author does not have a record. But still...
            self.print(f'Index error in attempting to read the pagination!', 2)
            page_to = 1

        # Preparing an empty list.
        s1, s2, s3, s4, s5, s6, s7, s8, s9 = [], [], [], [], [], [], [], [], []

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
            base = '//div[@class="row"]/div[@class="col-12"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//td[2]/a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # ISBN, author, publisher, page.
                b = a.xpath('.//td[2]')[0]
                x = self._book_heuristics_handler(b)
                s2.append(x['isbn'].replace('|', '').strip())
                s3.append(x['author'].strip())
                s4.append(x['publisher'].strip())
                s5.append(x['page'].strip())

                # Publish year.
                try:
                    s6.append(a.xpath('.//td[3]//strong[1]/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Publish location.
                try:
                    s7.append(a.xpath('.//td[3]//strong[2]/text()')[0].strip())
                except IndexError:
                    s7.append('')

                # Thumbnail (book's front cover image).
                try:
                    s8.append(a.xpath('.//td[1]/img/@src')[0].strip())
                except IndexError:
                    s8.append('')

                # Url.
                try:
                    s9.append(a.xpath('.//td[2]/a/@href')[0].strip())
                except IndexError:
                    s9.append('')

        self.print(
            f'({len(s1)}, {len(s2)}, {len(s3)}, {len(s4)}, {len(s5)}, {len(s6)}, {len(s7)}, {len(s8)}, {len(s9)})', 2
        )

        if not len(s1) == len(s2) == len(s3) == len(s4) == len(s5) == len(s6) == len(s7) == len(s8) == len(s9):
            raise MalformedDOMException(new_url)

        # Forge the Python dict.
        t = []
        for j in range(len(s1)):
            # Building the JSON dict.
            u = {}

            if '*' in fields or 'title' in fields:
                u['title'] = s1[j]

            if '*' in fields or 'isbn' in fields:
                u['isbn'] = s2[j]

            if '*' in fields or 'author' in fields:
                u['author'] = s3[j]

            if '*' in fields or 'publisher' in fields:
                u['publisher'] = s4[j]

            if '*' in fields or 'page' in fields:
                u['page'] = s5[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s6[j]

            if '*' in fields or 'location' in fields:
                u['location'] = s7[j]

            if '*' in fields or 'thumbnail' in fields:
                u['thumbnail'] = s8[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s9[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'isbn' in fields:
            d['isbn'] = s2

        if '*' in fields or 'author' in fields:
            d['author'] = s3

        if '*' in fields or 'publisher' in fields:
            d['publisher'] = s4

        if '*' in fields or 'page' in fields:
            d['page'] = s5

        if '*' in fields or 'year' in fields:
            d['year'] = s6

        if '*' in fields or 'location' in fields:
            d['location'] = s7

        if '*' in fields or 'thumbnail' in fields:
            d['thumbnail'] = s8

        if '*' in fields or 'url' in fields:
            d['url'] = s9

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d

    # noinspection PyDefaultArgument
    def scrape_garuda(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the Garuda journal information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "publisher"
        - "author"
        - "journal"
        - "doi"
        - "year"
        - "quartile"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not self.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_GARUDA.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="col-12"]/div[2]/div[2]/small/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())
            self.print('Detected number of pages: ' + str(page_to), 2)

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
            base = '//div[@class="row"]/div[@class="col-12"]//table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//td[2]/a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Publisher, author, journal name, and DOI.
                b = a.xpath('.//td[2]')[0]
                x = self._garuda_heuristics_handler(b)
                s2.append(x['publisher'].strip())
                s3.append(x['author'].strip())
                s4.append(x['journal'].strip())
                s5.append(x['doi'].strip())

                # Year.
                try:
                    s6.append(a.xpath('.//td[3]//strong/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Quartile.
                try:
                    s7.append(a.xpath('.//td[1]/div/text()')[0].strip())
                except IndexError:
                    s7.append('')

                # Url.
                try:
                    s8.append(a.xpath('.//td[2]/a/@href')[0].strip())
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

            if '*' in fields or 'publisher' in fields:
                u['publisher'] = s2[j]

            if '*' in fields or 'author' in fields:
                u['author'] = s3[j]

            if '*' in fields or 'journal' in fields:
                u['journal'] = s4[j]

            if '*' in fields or 'doi' in fields:
                u['doi'] = s5[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s6[j]

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

        if '*' in fields or 'publisher' in fields:
            d['publisher'] = s2

        if '*' in fields or 'author' in fields:
            d['author'] = s3

        if '*' in fields or 'journal' in fields:
            d['journal'] = s4

        if '*' in fields or 'doi' in fields:
            d['doi'] = s5

        if '*' in fields or 'year' in fields:
            d['year'] = s6

        if '*' in fields or 'quartile' in fields:
            d['quartile'] = s7

        if '*' in fields or 'url' in fields:
            d['url'] = s8

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d

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
        if not self.validate_author_id(l):
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
            self.print('Detected number of pages: ' + str(page_to), 2)

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
    def scrape_ipr(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the IPR information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "application_no"
        - "inventor"
        - "patent_holder"
        - "category"
        - "year"
        - "status"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not self.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_IPR.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="row"]/div[@class="col-6 text-right"]/small/i/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())
            self.print('Detected number of pages: ' + str(page_to), 2)

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
            base = '//div[@class="row"]/div[@class="col-12"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//td[1]/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Application number, inventor, and patent holder.
                b = a.xpath('.//td[1]')[0]
                x = self._ipr_heuristics_handler(b)
                s2.append(x['application_no'].strip())
                s3.append(x['inventor'].strip())
                s4.append(x['patent_holder'].strip())

                # Category.
                try:
                    s5.append(a.xpath('.//td[2]//strong[1]/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # Application year.
                try:
                    s6.append(a.xpath('.//td[2]//strong[2]/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Status.
                try:
                    s7.append(a.xpath('.//td[2]//strong[3]/text()')[0].strip())
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

            if '*' in fields or 'application_no' in fields:
                u['application_no'] = s2[j]

            if '*' in fields or 'inventor' in fields:
                u['inventor'] = s3[j]

            if '*' in fields or 'patent_holder' in fields:
                u['patent_holder'] = s4[j]

            if '*' in fields or 'category' in fields:
                u['category'] = s5[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s6[j]

            if '*' in fields or 'status' in fields:
                u['status'] = s7[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'application_no' in fields:
            d['application_no'] = s2

        if '*' in fields or 'inventor' in fields:
            d['inventor'] = s3

        if '*' in fields or 'patent_holder' in fields:
            d['patent_holder'] = s4

        if '*' in fields or 'category' in fields:
            d['category'] = s5

        if '*' in fields or 'year' in fields:
            d['year'] = s6

        if '*' in fields or 'status' in fields:
            d['status'] = s7

        if out_format == 'json':
            return t
        elif out_format == 'csv':
            return d

    # noinspection PyDefaultArgument
    def scrape_research(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the research information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "funds"
        - "program"
        - "schema"
        - "year"
        - "membership"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not self.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_RESEARCH.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="row"]/div[@class="col-6 text-right"]/small/i/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())
            self.print('Detected number of pages: ' + str(page_to), 2)

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
            base = '//div[@class="row"]/div[@class="col-12"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//td[1]/a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Funds, program, and schema.
                b = a.xpath('.//td[1]')[0]
                x = self._research_heuristics_handler(b)
                s2.append(x['funds'].strip())
                s3.append(x['program'].strip())
                s4.append(x['schema'].strip())

                # Publish year.
                try:
                    s5.append(a.xpath('.//td[2]//strong/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # Membership role.
                try:
                    s6.append(a.xpath('.//td[3]//strong/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Url.
                try:
                    s7.append(a.xpath('.//td[1]/a/@href')[0].strip())
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

            if '*' in fields or 'funds' in fields:
                u['funds'] = s2[j]

            if '*' in fields or 'program' in fields:
                u['program'] = s3[j]

            if '*' in fields or 'schema' in fields:
                u['schema'] = s4[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s5[j]

            if '*' in fields or 'membership' in fields:
                u['membership'] = s6[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s7[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'funds' in fields:
            d['funds'] = s2

        if '*' in fields or 'program' in fields:
            d['program'] = s3

        if '*' in fields or 'schema' in fields:
            d['schema'] = s4

        if '*' in fields or 'year' in fields:
            d['year'] = s5

        if '*' in fields or 'membership' in fields:
            d['membership'] = s6

        if '*' in fields or 'url' in fields:
            d['url'] = s7

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
        if not self.validate_author_id(l):
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
            self.print('Detected number of pages: ' + str(page_to), 2)

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
    def scrape_service(self, author_id: str, out_format: str = 'json', fields: list = ['*']):
        """ Scrape the community service information of one, and only one author in SINTA.
        Returns a Python array/list of dictionaries.

        The only supported out (return) formats are as follows:
        - "json" (includes both dict and list)
        - "csv" (stored as pandas DataFrame object)

        The fields that will be returned are as follows:
        - "*"
        - "title"
        - "funds"
        - "program"
        - "schema"
        - "year"
        - "membership"
        - "url"
        """
        l: str = str(author_id).strip()

        # Validating the output format.
        if out_format not in ['csv', 'json']:
            raise InvalidParameterException('"out_format" must be one of "csv" and "json"')

        # Validating the author ID.
        if not self.validate_author_id(l):
            raise InvalidAuthorIDException(l)

        # Try to open the author's specific menu page.
        url = self.URL_AUTHOR_SERVICE.replace('%%%', l)
        r = self._http_get_with_exception(url, author_id=author_id)

        self.print('Begin scrapping author ID ' + l + '...', 2)

        # Get the list of pagination.
        c = html.fromstring(r.text)
        try:
            s = c.xpath('//div[@class="row"]/div[@class="col-6 text-right"]/small/i/text()')[0]
            s = s.strip().split('|')[0].replace('Page', '').split('of')
            page_to = int(s[1].strip())
            self.print('Detected number of pages: ' + str(page_to), 2)

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
            base = '//div[@class="row"]/div[@class="col-12"]/table[@class="table"]//tr'
            c_base = c.xpath(base)

            for a in c_base:
                # Title.
                try:
                    s1.append(a.xpath('.//td[1]/a/text()')[0].strip())
                except IndexError:
                    s1.append('')

                # Funds, program, and schema.
                b = a.xpath('.//td[1]')[0]
                x = self._service_heuristics_handler(b)
                s2.append(x['funds'].strip())
                s3.append(x['program'].strip())
                s4.append(x['schema'].strip())

                # Publish year.
                try:
                    s5.append(a.xpath('.//td[2]//strong/text()')[0].strip())
                except IndexError:
                    s5.append('')

                # Membership role.
                try:
                    s6.append(a.xpath('.//td[3]//strong/text()')[0].strip())
                except IndexError:
                    s6.append('')

                # Url.
                try:
                    s7.append(a.xpath('.//td[1]/a/@href')[0].strip())
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

            if '*' in fields or 'funds' in fields:
                u['funds'] = s2[j]

            if '*' in fields or 'program' in fields:
                u['program'] = s3[j]

            if '*' in fields or 'schema' in fields:
                u['schema'] = s4[j]

            if '*' in fields or 'year' in fields:
                u['year'] = s5[j]

            if '*' in fields or 'membership' in fields:
                u['membership'] = s6[j]

            if '*' in fields or 'url' in fields:
                u['url'] = s7[j]

            t.append(u)

        # Forge the pandas DataFrame object.
        # Building the CSV dict.
        d = {}
        if '*' in fields or 'title' in fields:
            d['title'] = s1

        if '*' in fields or 'funds' in fields:
            d['funds'] = s2

        if '*' in fields or 'program' in fields:
            d['program'] = s3

        if '*' in fields or 'schema' in fields:
            d['schema'] = s4

        if '*' in fields or 'year' in fields:
            d['year'] = s5

        if '*' in fields or 'membership' in fields:
            d['membership'] = s6

        if '*' in fields or 'url' in fields:
            d['url'] = s7

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
        if not self.validate_author_id(l):
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
            self.print('Detected number of pages: ' + str(page_to), 2)

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
