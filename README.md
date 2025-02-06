# sintautils

Python utility package for retrieving and synchronizing data on [SINTA (Science and Technology Index)](https://sinta.kemdikbud.go.id)

## A. Documentation

### A.1. Installation

You can install `sintautils` using PIP as follows:

```sh
pip install sintautils
```

### A.2. Author Verification

#### A.2.i. Authentication

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

#### A.2.ii. Basic Usage

After importing the modules and initializing the `AV` class, you can start dumping research information of a given author in SINTA using the `dump_author()` method. The following code dumps all research data pertaining to a SINTA author and saves the result to an Excel file named `sintautils_dump_author-1234.xlsx` under the current working directory. Each data category (IPR, book, Google Scholar publication, etc.) is represented by a separate Excel sheet.

```python
# Change "1234" to the respective author's SINTA ID.
scraper.dump_author('1234')
```

You can customize which data type to scrape by specifying the `fields` parameter:

```python
# Possible values for the "fields" parameter:
# book, garuda, gscholar, ipr, research, scopus, service, wos
# Use asterisks "*" (the default) in order to scrape all information.
scraper.dump_author('1234', fields='book garuda wos')
```

Also, you can change the output format, save directory, and filename prefix as follows:

```python
# Possible values for the "out_format" parameter:
# csv, json, json-pretty, xlsx
scraper.dump_author('1234',
    out_format='json-pretty',
    out_folder='/path/to/save/directory',
    out_prefix='filename_prefix-'
)
```

If multiple fields are specified when using `out_format=csv`, each data type will be saved as a separate CSV file under the same `out_folder` directory.

#### A.2.iii. Author Data Synchronization

Using `sintautils`, you can programmatically sync author publication and profile data using OOP-style commands. Below are some examples to sync author data:

```python
# Sync Google Scholar publication data.
scraper.sync_gscholar(author_id='1234')

# Sync multiple author IDs at once.
scraper.sync_gscholar(author_id=['1234', '5678'])
```

To sync an author's profile information with the information stored in [DIKTI's data center](https://pddikti.kemdiktisaintek.go.id/), use the following command:

- `scraper.sync_dikti(author_id=...)`

To sync an author's specific publication type (Garuda, Google Scholar, Scopus, and Web of Science), use the following command:

- `scraper.sync_garuda(author_id=...)`
- `scraper.sync_gscholar(author_id=...)`
- `scraper.sync_scopus(author_id=...)`
- `scraper.sync_wos(author_id=...)`

Also, you can sync an author's research and community service data with the information stored in [BIMA's data center](https://bima.kemdikbud.go.id/) as follows:

- `scraper.sync_research(author_id=...)`
- `scraper.sync_service(author_id=...)`

## B. To-Do

### B.1. New Features

**v0.0.1**

- [X] Add scopus, comm. service, and research scraper of each author.
- [X] Add scopus, research and comm. service sync per author.
- [X] Add scraper for IPR and book of each author.
- [X] Add garuda scraper per author.
- [X] Add author info dumper.
- [X] Add author info dumper using `openpyxl` implementation that outputs to an Excel/spreadsheet workbook file.

**v0.0.2**

- [ ] Add non-AV SINTA login mechanism.
- [ ] Add non-AV SINTA study programs data scraper.
- [ ] Add non-AV SINTA authors data scraper.

### B.2. Bug Fixes

**v0.0.1**

- [X] Google Scholar scraper: no publication case.

### B.3. Improvements

**v0.0.1**

- [X] Bulk scraping of author list: return a dict with each author ID as key instead of just a plain list.
- [X] Move `_scrape_scopus`, `_scrape_wos` etc. functions to `backend.py`.

**v0.0.2**

- [ ] Add the functionality to inflate bulk-scraping of multiple authors into a single XLSX file.
- [X] Add `str()` cast in the SINTA ID parameter, especially in `dump_author()`.
- [X] Extend the `requests` timeout duration.
- [X] Remove duplicates from the SINTA ID parameter.
- [X] Add trailing and leading whitespace stripper in the author ID parameter handler of backend syncer.
- [X] Enable the default option for author dumper option to save files as the author's full name.

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
