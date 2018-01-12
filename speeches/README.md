### To Run Speech Scraper
Make sure you have `Python 3` installed and the packages `requests` and `BeautifulSoup` installed then run
`python speech_scraper.py`
and it will output a file called `election_speeches.json` into the current directory with the following format for each speech:

* Name: Candidate's name
* Title: Title of the speech from the "American Presidency Project" website
* Year: Year of the speech (eg. 2007)
* Month: Month of the speech (eg. 01, 02 etc)
* Day: Day of the speech (eg 01, 31 etc)
* Text: Full text of the speech
