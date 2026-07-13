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

# for i in range(len(table_hour_list_container)):
#     print(f"DATAFRAME {i}:")
#     with pd.option_context('display.max_columns', None):
#         print(df_list[i])
#     print("\n")
