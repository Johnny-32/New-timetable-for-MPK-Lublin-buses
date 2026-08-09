# New timetable for MPK Lublin buses
This project aims to make a better looking and simpler timetable for MPK Lublin buses and also show some cool and useful features based on it.

## Technologies
- Python 3.14
- HTML, CSS

## How it works
- Getting an .html file from the MPK Lublin website using [requests](https://pypi.org/project/requests/)
- Parsing a table from an .html file using [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- Manipulating the data, so that it can be exported to html using [Jinja2](https://jinja.palletsprojects.com/)
- Calculating frequencies on the specific line, the stop and time of day, using my own algorithm

## To do:
- See if shortened and transposed timetables can be made from lists of dicts instead of df's
- Make a Vienna style timetable, then a variation of Munich's, and maybe make a Copenhagen style timetable for the whole route
- Test frequency algorithm on a variety of MPK Lublin lines and stops (including these in non-holiday timetables)
- A website that will display a specific timetable picked by an user, in an html format with an option to export to pdf in a print-friendly format
- Add retrieving data from GTFS instead of .html
- Make a tier list with bus lines (separate tier list for each time ex. weekdays and then maybe group them into categories for ex. key lines have a frequency of 15 minutes during rush hour, 30 minutes on saturdays...)


### Maybe in the distant future
- Add timetables in different formats for example:
  - MPK Lublin style - with columns corresponding to different hours
  - SL Stockholm style - one timetable for the whole line with departure times only for most important stops and departures that are read like a book (from left to right and top to bottom)
- A section that let's user pick two bus stops and then show all departures from A to B and B to A and their corresponding lengths (maybe I'll add a timer that will show time to a next departure)
- Add realtime departure board for stops and for routes 

## Usage
Will be updated in the future.
