# sintautils

Python utility package for scraping information on SINTA (Science and Technology Index)

## A. Documentation

### A.1. Author Verification

#### A.1.i. Authentication

Author verification menu is a restricted menu of SINTA. You must be registered as a university administrator and obtain an admin credential in order to use this function. An author verification (AV) admin's credential consists of an email-based username and a password.

To use the AV scraper, you must first import it. And then, a scraper object called `AV` must be initialized and passed with AV admin's username and password. Finally, perform login using the scarper object in order to retrieve `requests` session cookie with the SINTA host.

```python
from sintautils import AV
scraper = AV('admin@university.edu', 'password1234')
scraper.login()
```

This can be done in two lines as follows:

```python
from sintautils import AV
scraper = AV('admin@university.edu', 'password1234', autologin=True)
```

## B. To-Do

### B.1. New Features

- [X] Add scopus, comm. service, and research scraper of each author.
- [ ] Add scopus, research and comm. service sync per author.
- [ ] Add scraper for all IPR and book.
- [ ] Add garuda scraper per author.

### B.2. Bug Fixes

- [X] Google Scholar scraper: no publication case.

### B.3. Improvements

- [ ] Bulk scraping of author list: return a dict with each author ID as key instead of just a plain list.
- [X] Move `_scrape_scopus`, `_scrape_wos` etc. functions to `backend.py`.

## C. License Notice

```
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>. 
```
