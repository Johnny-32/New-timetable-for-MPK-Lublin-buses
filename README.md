# New timetable for MPK Lublin buses
This project aims to make a better looking and simpler timetable for MPK Lublin buses and also show some cool and useful features based on it.

## Technologies
- Python 3.14

## How it works
This project is centered around a single python file that has diffrent functions:
- Getting an html from the MPK Lublin website using [requests](https://pypi.org/project/requests/)
- Parsing a table from an html file using [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/)
- Converting the data, so that it can be converted to a [Pandas](https://pandas.pydata.org/docs/index.html) dataframe
- Deleting unnecessary columns, so that the timetable is simpler and takes less space 

## To do:
- Fix timetable being shifted by one to the left, beacuse of reading empty columns
- A webiste that will display a specific timetable picked by an use (if it will proves to be easy, I'll add a timetable conversion to PDF in an easy to print format)
- Make a tier list with bus lines (seperate tier list for each time ex. weekdays and then maybe group them into categories for ex. key lines have a frequency of 15 minutes during rush hour, 30 minutes on saturdays...)
- Maybe - a section that let's user pick two bus stops and then show all departures from A to B and B to A and their corresponding lengths (maybe I'll add a timer that will show time to a next departure)

## Usage
As of now just download main.py file and run it however you like (CLI, Text editor, IDE).
