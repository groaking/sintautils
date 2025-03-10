# `sintautils` Project Change Log

## v.0.0.2 2025.02.06 (2)

:star2: **NEW**

- Added PDDIKTI profile data synchronizer
- Added BIMA research and community service data synchronizer
- Added Garuda, Google Scholar, Scopus, and Web of Science (WOS) data synchronizer

:four_leaf_clover: **IMPROVEMENT**

- Added trailing and leading whitespace stripper in the author ID parameter handler of backend syncer.
- Implemented timeout flag in the `requests` HTTP requests.
- Implemented `str()` cast for integer inputs in `author_id` parameters.
- Removed duplicate author ID from list arguments in the scraper/syncer functions.
- Enabled the default option for author dumper option to save files as the author's full name.

## v0.0.1 2025.01.30 (1)

:information_source: **INFO**

- This is the very first PyPI release of `sintautils`.

:star2: **NEW**

- Added Scopus, Google Scholar, Garuda, and WOS data scraper for individual authors.
- Added book, IPR, research, and community service data scraper for individual authors.
- Added author data dumper that outputs into CSV, JSON, and XLSX files.
