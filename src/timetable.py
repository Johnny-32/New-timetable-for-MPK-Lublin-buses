from functools import lru_cache

import pandas as pd
import requests
from bs4 import BeautifulSoup
from jinja2 import Template

@lru_cache(maxsize=32)
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

# Shortening the number of columns (ex. if hour 10, 11, 12 have the same departure minutes we can combine them into one column 10-12)

def make_a_dict_list_short(url):
    dict_container = make_a_dict_list(url)
    dict_container_short = []

    for current_dict_list in dict_container:
        current_tuple_list = list(current_dict_list.items())

        new_dict = {}
        i = 0
        n = len(current_tuple_list)

        while i < n:
            start_tuple = current_tuple_list[i]
            j = i + 1

            while j < n and start_tuple[1] == current_tuple_list[j][1]:
                j += 1

            end_tuple = current_tuple_list[j - 1]
            new_dict_key, new_dict_val = start_tuple

            if j - i > 1:
                start_key, _ = start_tuple
                end_key, _ = end_tuple
                new_dict_key = f"{start_key}-{end_key}"

            new_dict[new_dict_key] = new_dict_val

            i = j

        dict_container_short.append(new_dict)

    return dict_container_short

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

def parse_stop_name(url):
    soup = make_a_request(url)

    return soup.select_one("div.rozklad-przystanek > b > a").text.split("-")[1].strip()

def parse_stop_id(url):
    soup = make_a_request(url)

    return soup.select_one("div.rozklad-przystanek > b > a").text.split("-")[0].strip()

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
        stop_name = parse_stop_name(url),
        stop_id = parse_stop_id(url)
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    return html_out

url = "https://mpk.lublin.pl/?przy=1022&lin=032"

export_to_template(url)
