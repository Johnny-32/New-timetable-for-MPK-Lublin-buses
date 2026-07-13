import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://mpk.lublin.pl/?przy=1022&lin=032"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"
    html_content = response.text

except requests.exceptions.HTTPError as errh:
    print(f"Błąd HTTP (np. złe uprawnienia, brak strony): {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"Błąd połączenia (np. problem z internetem, błędny URL): {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Serwer nie odpowiedział w określonym czasie: {errt}")
except requests.exceptions.RequestException as err:
    print(f"Coś poszło nie tak: {err}")

soup = BeautifulSoup(html_content, "html.parser")

# Table titles

span_list_temp = soup.find_all('span', class_="rozklad-title")
span_list = [span.get_text() for span in span_list_temp]

# Parsing table header row

table_list = soup.find_all('table')

# table_0 = soup.find('table').prettify()
# print(table_0)

table_hour_list_th_temp = soup.find_all('th')
table_hour_list_th_temp2 = [table_hour.get_text() for table_hour in table_hour_list_th_temp]
table_hour_list_th = [table_hour.replace("\t", "").replace("\r", "").replace("\n", "") for table_hour in table_hour_list_th_temp2]

# Up to this point we have one list with all the headers, now i'm going to split this list into smaller sections, seperate for each table

table_hour_list_container = []
table_hour_list = []
godz_counter = 0

for elem in table_hour_list_th:
    if elem == "Godz.":
        godz_counter += 1
        if (godz_counter > 1):
            table_hour_list_container.append(table_hour_list)
            table_hour_list = []
    else:
        table_hour_list.append(elem)
table_hour_list_container.append(table_hour_list)

# Parsing table contents

table_minute_list_td = soup.find_all("td")
table_minute_list_td = [table_minute_one_hour_list.get_text() for table_minute_one_hour_list in table_minute_list_td]
table_minute_list_td = [table_minute_one_hour_list.replace("\t", "").replace("\r", "").replace("\n", "") for table_minute_one_hour_list in table_minute_list_td]

# print(table_minute_list_td)

# Removing leading and trailing whitespaces

table_minute_list_td = [table_minute_one_hour_list.strip() for table_minute_one_hour_list in table_minute_list_td]
# print(table_minute_list_td)

# Dividing list elements into proper minute marks (ex. "003259" -> "00", "32", "59")

table_minute_list_td_clean = []
table_minute_list_one_schedule_td_clean = []
table_minute_list_one_hour_td_clean = []
min_counter = 0

for table_minute_one_hour_list in table_minute_list_td:
    if table_minute_one_hour_list.isnumeric():
        number_of_groups = len(table_minute_one_hour_list) // 2
        for i in range(number_of_groups):
            first_position = 2 * i
            table_minute_list_one_hour_td_clean.append(table_minute_one_hour_list[first_position:first_position + 2])
        table_minute_list_one_schedule_td_clean.append(table_minute_list_one_hour_td_clean)
        table_minute_list_one_hour_td_clean = []
    else:
        if table_minute_one_hour_list:
            min_counter += 1
            if min_counter >= 2:
                table_minute_list_td_clean.append(table_minute_list_one_schedule_td_clean)
                table_minute_list_one_schedule_td_clean = []
        else:
            table_minute_list_one_hour_td_clean.append(table_minute_one_hour_list)
            table_minute_list_one_schedule_td_clean.append(table_minute_list_one_hour_td_clean)
            table_minute_list_one_hour_td_clean = []

table_minute_list_td_clean.append(table_minute_list_one_schedule_td_clean)
table_minute_list_one_schedule_td_clean = []

# print(table_hour_list_container[0])
# print("\n")
# print(table_minute_list_td_clean[0])

# Making dictionaries with hours as keys and list of minutes as values (ex. '5': ['00', '32', '59'])

table_dict = []
table_dict_container = []
for i in range(len(table_hour_list_container)):
    table_dict = dict(zip(table_hour_list_container[i], table_minute_list_td_clean[i]))
    table_dict_container.append(table_dict)

# print(table_dict_container[0])

# Adding Nan's to hours that don't have any departures

for table_dict in table_dict_container:
    for key, elem in table_dict.items():
        if len(elem) == 1 and '' in elem:
            table_dict[key] = [float('nan')]


# Adding Nan's so that I can make a proper df, beacuse all lists must be of the same length

for table_dict in table_dict_container:
    m = len(max(table_dict.values(), key=len))
    for elem in table_dict.values():
        while len(elem) < m:
            elem.append(float("nan"))

# print(table_dict_container)

# print(table_dict_container[0])

# Creating df's with header row and deleting indexes

df_list = []
for i in range(len(table_hour_list_container)):
    df_list.append(pd.DataFrame(table_dict_container[i]))
    df_list[i].index = [''] * len(df_list[i])

# Shortening the number of columns (ex. if hour 10, 11, 12 have the same departure minutes we can combine them into one column 10-12)

for idx in range(len(df_list)):
    current_df = df_list[idx]
    cols = list(current_df.columns)
    
    new_df_data = {} 
    
    i = 0
    while i < len(cols):
        start_col = cols[i]
        end_col = start_col
        
        j = i + 1
        while j < len(cols):
            if current_df[start_col].equals(current_df[cols[j]]):
                end_col = cols[j]
                j += 1
            else:
                break
        
        if start_col != end_col:
            new_name = f"{start_col}-{end_col}"
        else:
            new_name = str(start_col)
            
        new_df_data[new_name] = current_df[start_col]
        i = j

    df_list[idx] = pd.DataFrame(new_df_data)

# Printing dataframes to the console

for i in range(len(table_hour_list_container)):
    print(f"DATAFRAME {i}:")
    with pd.option_context('display.max_columns', None):
        print(df_list[i])
    print("\n")

# Calculating approximate frequencies
# The algorithm will work by:
# 1. Reading values of two minute values at a time and then calculating the frequency by subtracting each minute with the next 
#    and adding 60 to the result if it's a non-positive number, so that the algorithm works with subtracting minutes that are associated with different hours,
#    results will be stored in a dictionary with key that indicates hours and minutes that the minutes were subtracted (ex. 5:09 and 5:39 -> '5:09 - 5:39': '30') (ex. 5:39 and 6:09 -> '5:39 - 6:09': '30')
#ex. 1.1  6   mod 60 (59 - 29) = 30
#         29
#         59
# 
# ex. 1.2  5   6   27 - 29 = -2 (beacuse it's a non-positive number we add 60 the the result) -2 + 60 = 58
#         29  27
# 
# 2. To have a x minute frequency label the line needs to have departures every x +- y minutes,
#    where x is the frequency and y is the tolerance for said frequency
#    for ex. if a line has a 24 minute fruquency label it needs to have departures every 22-26 minutes, if tolerance is 2 minutes,
#    as a base a tolerance of 2 minutes will be used,
#    frequency for a period of time must be one of the predefined frequencies:
#    (15, 20, 24, 30, 40, 60, >60)
#    ??? Maybe if a frequency for a period of time sways to far from a predefined frequency it will be put into something like this:
#    if a calculated frequency is 35 minutes with big fluctuations, maybe it can be put into 30-40 frequency
#    
# 3. The differences will be put into groups based on their differences, if the difference between two diiferences is <= tolerance 
#    and it the diff of diffs. is within tolerance of a predefined frequency these differences will be put in a group
# 
# 4. To end a group, a difference between differences needs to be larger than the tolerance
#    To start another group the diff between diffs. needs to fall be <= tolerance
#    ??? If it isn't then probably we'll need to up the tolernace temporarily
# 
# 5. From these groups we can skip "End of group 1." relation and pick the last from difference from group x and the first from group x+1, we'll refer to them as key differences
# 
# 6. Using these two differences we can make out a breakpoint between two frequency groups by checking the keys from key differences 
#    and extracting the first timestamp from the first key difference and the second timestamp from the second one, in result we we'll have a breakpoint
# 
# 7. At the end we can plot the data into something like this: first departure - frequency - breakpoint - frequency - breakpoint - ... - frequency - last departure
# 
# 
# The labels will be put into two main categories:
# 1. The labels will be most often a number that is obtained by dividing 60 by the number of the departures (ex. 60 min. / 2 dep. = 30 min. frequency)
#    So these labels will be 15, 20, 30, 60, less often than 1 hour, [...] 2 hours, [...] 3 hours
# 
# 2. The labels can also have a number that is obtained by dividing 120 60 by the number of the departures (ex. 120 min. / 3 dep. = 40 min. frequency)
#    So these labels will be 24, 40 minutes
# 
# 
# Example 1. (Made in July 2026 - Holiday timetable) ------------------------------------------------------------------------------------------------
# Line: 32
# Direction: Daszyńskiego
# Bus stop: Plac Litewskiego 02 (Index - 1022)
# Timetable:
# 
#     5   6    7    8   9   10  11   12  13   14  15   16   17   18   19   20   21   22   23 
#    05  07   26   15  02   14  02   14  02   14  02   17   04   05   03   03   06   06   05
#    37  34   51   38  26   38  26   38  26   38  29   41   35   33   33   36   36   36  NaN
#   NaN  59  NaN  NaN  50  NaN  50  NaN  50  NaN  53  NaN  NaN  NaN  NaN  NaN  NaN  NaN  NaN
# 
# In this example we will be sticking to hours 5-9
# 1. Calculating differences
# 5:37 - 5:05 = 32
# 6:07 - 5:37 = -30 + 60 = 30
# 6:34 - 6:07 = 27
# 6:59 - 6:34 = 25
# 7:26 - 6:59 = -33 + 60 = 27
# 7:51 - 7:26 = 25
# 8:15 - 7:51 = -36 + 60 = 24
# 8:38 - 8:15 = 23
# 9:02 - 8:38 = 24
# 9:26 - 9:02 = 24
# 9:50 - 9:26 = 24
# 
# So using our common sense we can see that frequencies are:
# 5:05 - 6:07 --- 30 minutes
# 6:07 - 7:51 --- it makes to make it 24 minutes, but in reality it's 26 minutes
# 7:51 - 9:50 --- 24 minutes
# 
# Now we can group the differences, let's say that the tolerance between differences is 2 minutes
# 32 - 30 = 2 -> Start of group 1.
# 30 - 27 = 3 -> End of group 1.
# 27 - 25 = 2 -> Start of group 2.
# 25 - 27 = 2 -> Both in group 2.
# 27 - 25 = 2 -> Both in group 2
# 25 - 24 = 1 -> Both in group 2
# 24 - 23 = 1 -> Both in group 2
# 23 - 24 = 1 -> Both in group 2
# 24 - 24 = 0 -> Both in group 2
# 24 - 24 = 0 -> Both in group 2
# 
# So now we have 2 groups and now we can calculate the mean from all values in each group and see which predefined frequency (for ex. 20, 24, 30, ...) will be the closest to the mean and assign that label
# for ex. group 1. (32 + 30) / 2 = 31 -> which is close to 30, so we will asign a 30 minute frequency label to that group
# group 2. after calculations will have 24 minute frequency label
# 
# We can see that the last difference for the group 1 is 30, and the first for the group 2. is 27,
# so that means if we skip "End of group 1." we have all the differences in correct groups (obviously we need to delete duplicates)
# 
# Now we need to extract timestamps from key differences (30 and 27)
# We can do this by - extracting the key from dictionary:
# in group 1. we have a key difference of 30, which translates to 6:07 - 5:37
# in group 2. we have a key difference of 27, which translates to 6:34 - 6:07
# 
# Beacuse the first number of the 1. group and the second number of the 2. group matches, that means that 6:07 will be a breakpoint for frequency labels
# 
# As a result we got frequencies which are the same as we got above using common sense
# 
# ??? Maybe add calculating frequencies by getting the timetable from the first stop of a route, beacuse the departures there are more consistent