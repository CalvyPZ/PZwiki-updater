# PZwiki-updater
A group of pywikibot scripts used to update PZwiki based on parser output.

# Config
In `updater.py` there are various config options based on the desired result.

* cpu_threads: Default `8`, effects multithreading for searching.
* rate_limit: Default `0`, set to desired rate limit if required.
* default_language: Default `en`, shouldn't need changing
* language_pages: Default `False`, set `True` to update language subpages.
* parser_output_path: Set to the `/output` directory of your parser.
* hitory_path: Set to the `/txt` directory of history creator.
* test_mode: Default `False`, set `True` to only edit the test page.
* test_page: Set the page to be edited if test mode is enabled.

## Orchestrator options
Controls which parts of the updater should or shouldn't run. All `True` by default.

# Usage
* Put the `updater.py` script and `updater_modules` folder into your userscripts pywikibot folder
* Run `updater.py` via `pwb.py`
