import pandas as pd
import requests
from bs4 import BeautifulSoup
from jinja2 import Template

def make_a_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Website parsing error: {e}")
        return None

    return BeautifulSoup(response.text, "html.parser")


def make_a_span_list(url):
    soup = make_a_request(url)

    # Table titles

    span_list = soup.find_all('span', class_="rozklad-title")
    span_list = [span.get_text() for span in span_list]

    return span_list

def make_a_dict_list(url):
    soup = make_a_request(url)

    # Parsing table header row

    table_list = soup.find_all('table')

    table_hour_list_th_temp = soup.find_all('th')
    table_hour_list_th_temp2 = [table_hour.get_text() for table_hour in table_hour_list_th_temp]
    table_hour_list_th = [table_hour.replace("\t", "").replace("\r", "").replace("\n", "") for table_hour in
                          table_hour_list_th_temp2]

    # Up to this point we have one list with all the headers, now I'm going to split this list into smaller sections, separate for each table

    table_hour_list_container = []
    table_hour_list = []
    godz_counter = 0

    for elem in table_hour_list_th:
        if elem == "Godz.":
            godz_counter += 1
            if godz_counter > 1:
                table_hour_list_container.append(table_hour_list)
                table_hour_list = []
        else:
            table_hour_list.append(elem)
    table_hour_list_container.append(table_hour_list)

    # Parsing table contents

    table_minute_list_td = soup.find_all("td")
    table_minute_list_td = [table_minute_one_hour_list.get_text() for table_minute_one_hour_list in
                            table_minute_list_td]
    table_minute_list_td = [table_minute_one_hour_list.replace("\t", "").replace("\r", "").replace("\n", "") for
                            table_minute_one_hour_list in table_minute_list_td]

    # Removing leading and trailing whitespaces

    table_minute_list_td = [table_minute_one_hour_list.strip() for table_minute_one_hour_list in table_minute_list_td]

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
                table_minute_list_one_hour_td_clean.append(
                    table_minute_one_hour_list[first_position:first_position + 2])
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

    # Making dictionaries with hours as keys and list of minutes as values (ex. '5': ['00', '32', '59'])

    table_dict_list = []
    for i in range(len(table_hour_list_container)):
        table_dict = dict(zip(table_hour_list_container[i], table_minute_list_td_clean[i]))
        table_dict_list.append(table_dict)

    return table_dict_list


def make_a_df_list(url):
    table_dict_list = make_a_dict_list(url)

    # Adding Nan's to hours that don't have any departures

    for table_dict in table_dict_list:
        for key, elem in table_dict.items():
            if len(elem) == 1 and '' in elem:
                table_dict[key] = [float('nan')]


    # Adding Nan's so that I can make a proper df, because all lists must be of the same length

    for table_dict in table_dict_list:
        m = len(max(table_dict.values(), key=len))
        for elem in table_dict.values():
            while len(elem) < m:
                elem.append(float("nan"))

    # Creating df's with header row and deleting indexes

    df_list = []
    for i, table_dict in enumerate(table_dict_list):
        df_list.append(pd.DataFrame(table_dict_list[i]))
        df_list[i].index = [''] * len(df_list[i])

    return df_list

# Shortening the number of columns (ex. if hour 10, 11, 12 have the same departure minutes we can combine them into one column 10-12)

def make_a_df_list_short(url):

    df_list = make_a_df_list(url)

    df_list_short = []

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

        df_list_short.append(pd.DataFrame(new_df_data))

    return df_list_short

# Transposing df's

def make_a_df_list_transposed(url):

    df_list = make_a_df_list(url)

    df_list_transposed = []
    for idx in range(len(df_list)):
        df_list_transposed.append(df_list[idx].transpose())

    return df_list_transposed

# Return a date that's either in an ISO format or in a dot format (DD.MM.YYYY)

def parse_timetable_valid_from(url, iso_format = True):
    soup = make_a_request(url)

    temp = soup.select_one('div[align="right"]').text.split()[-1]

    if iso_format:
        return temp
    else:
        year, month, day = temp.split("-")
        dot_format_date = f"{day}.{month}.{year}"
        return dot_format_date

def parse_street_names(url):
    soup = make_a_request(url)

    return soup.select_one("center > strong").text

def parse_line(url):
    part_url = url.split("?")[1]
    return part_url.split("=")[2].lstrip("0")

def parse_destination(url):
    soup = make_a_request(url)

    return soup.find("div", class_="rozklad-kierunek").text.split()[1]

def parse_stop(url):
    soup = make_a_request(url)

    return soup.select_one("div.rozklad-przystanek > b > a").text.strip()

def export_to_template(url, output_path="../web/test.html"):
    with open("../web/template.html", encoding="utf-8") as f:
        template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)

    html_out = template.render(
        table_dict_list = make_a_dict_list(url),
        span_list = make_a_span_list(url),
        timetable_valid_from = parse_timetable_valid_from(url, iso_format=False),
        street_names = parse_street_names(url),
        line = parse_line(url),
        destination = parse_destination(url),
        stop = parse_stop(url)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    return html_out


url = "https://mpk.lublin.pl/?przy=1022&lin=032"

# print(parse_timetable_valid_from(url, iso_format=False))