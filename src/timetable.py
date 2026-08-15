import os.path
import re
from functools import lru_cache
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
import tkinter as tk
from tkinter import filedialog

@lru_cache(maxsize=32)
def make_a_request(url, html5lib_parser = False):
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

    if not html5lib_parser:
        return BeautifulSoup(response.text, "html.parser")

    return BeautifulSoup(response.text, "html5lib")


def make_a_span_list(url):
    soup = make_a_request(url)

    # Table titles

    span_list = soup.find_all('span', class_="rozklad-title")
    span_list = [span.get_text() for span in span_list]

    return span_list

def make_a_dict_list(url):
    soup = make_a_request(url)

    # Parsing table header row

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
        if not "Min." in table_minute_one_hour_list:

            # Group is for ex. 00 or 32a
            group = ""

            for idx in range(len(table_minute_one_hour_list)):
                next_idx = idx + 1
                if table_minute_one_hour_list[idx].isnumeric():
                    group += table_minute_one_hour_list[idx]
                    if (len(group) == 2 and (next_idx < len(table_minute_one_hour_list))
                            and table_minute_one_hour_list[next_idx].isnumeric()):
                        table_minute_list_one_hour_td_clean.append(group)
                        group = ""

                if not table_minute_one_hour_list[idx].isnumeric():
                    group += table_minute_one_hour_list[idx]
                    table_minute_list_one_hour_td_clean.append(group)
                    group = ""

            if group:
                table_minute_list_one_hour_td_clean.append(group)

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

    temp = soup.select_one('div[align="right"]').get_text(strip=True).split()[-1]

    if iso_format:
        return temp
    else:
        year, month, day = temp.split("-")
        dot_format_date = f"{day}.{month}.{year}"
        return dot_format_date

def parse_street_names(url):
    soup = make_a_request(url)

    return soup.select_one("center > strong").get_text(strip=True)

def parse_line(url):
    part_url = url.split("?")[1]
    return part_url.split("=")[2].lstrip("0")

def parse_destination(url):
    soup = make_a_request(url)

    return soup.find("div", class_="rozklad-kierunek").text.replace("Kierunek:", "").strip()

def parse_stop_name(url):
    soup = make_a_request(url)

    return soup.select_one("div.rozklad-przystanek > b > a").get_text(strip=True).split("-")[1].strip()

def parse_stop_id(url):
    soup = make_a_request(url)

    return soup.select_one("div.rozklad-przystanek > b > a").get_text(strip=True).split("-")[0].strip()

def parse_stops(url):
    soup = make_a_request(url)

    stop_list = [
        a.get_text(strip=True)
        for a in soup.select("ul.rozklad-mapa > li:not(.ulica) > a")
    ]

    return stop_list

# Returns a dict with street names as keys and stop lists values
# ex. {"street1": ["stop1", "stop2"], ...}

def parse_stops_and_streets(url, strip_stop_id=True):
    soup = make_a_request(url, html5lib_parser=True)

    li_list = [li for li in soup.select("ul.rozklad-mapa > li")]

    street_name_sublist = []
    stop_and_street_dict = {}
    current_street = None

    for li in li_list:
        if "ulica" in li.get("class", []):
            if street_name_sublist:
                stop_and_street_dict[current_street] = street_name_sublist
                street_name_sublist = []

            current_street = li.get_text(strip=True)
        else:
            stop_name = li.find("a").get_text(strip=True)
            if strip_stop_id:
                stop_name = stop_name.split("-", 1)[1].strip()
            street_name_sublist.append(stop_name)

    if current_street and street_name_sublist:
        stop_and_street_dict[current_street] = street_name_sublist

    return stop_and_street_dict

def parse_period(url):
    span_list = make_a_span_list(url)

    for span in span_list:
        if "DZIEŃ POWSZEDNI" in span:
            return span.split(",")[1]

    return None

def make_a_better_span_list(url):
    period = parse_period(url)
    span_list = make_a_span_list(url)
    new_span_list = []

    for span in span_list:
        if period in span:
            new_span = span.split(",")[0]
            new_span_list.append(new_span)
        else:
            new_span_list.append(span)

    return new_span_list

def parse_special_departures_texts(url):
    soup = make_a_request(url)
    div = soup.select_one("div#middle-area")

    direct_texts = div.find_all(string=True, recursive=False)
    direct_texts = [s.strip() for s in direct_texts]

    list_of_special_departure_texts = []

    for text in direct_texts:
        if text and text[0].isalpha():
            list_of_special_departure_texts.append(text)

    return list_of_special_departure_texts


def render_to_file(template_path, output_path, **context):
    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read(), trim_blocks=True, lstrip_blocks=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(template.render(**context))

def export_to_template(
        url,
        html_template="../web/template.html",
        html_out="../web/test.html",
):
    render_to_file(
        html_template, html_out,
        table_dict_list = make_a_dict_list(url),
        special_departures = parse_special_departures_texts(url),
        span_list = make_a_better_span_list(url),
        timetable_valid_from = parse_timetable_valid_from(url, iso_format=False),
        stops_and_streets = parse_stops_and_streets(url),
        line = parse_line(url),
        destination = parse_destination(url),
        stop_name = parse_stop_name(url),
        stop_id = parse_stop_id(url),
        period = parse_period(url)
    )


def html_to_pdf(html_path="../web/test.html", pdf_path="../web/test.pdf"):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.pdf(path=pdf_path, landscape=True, print_background=True)
        browser.close()


url = "https://mpk.lublin.pl/?przy=1022&lin=032"
# url = "https://mpk.lublin.pl/?przy=2122&lin=039"

export_to_template(url)
html_to_pdf()

# if __name__ == "__main__":
#     print("Enter the url of a timetable you want to generate:")
#     url = input()
#
#     # RegEx that will check if the url has a proper structure, it doesn't check whether the url exists
#
#     pattern = r"^(https://mpk\.lublin\.pl/\?przy=\d{4}&lin=[0-9A-Z]{3})"
#
#     url_proper_structure = re.search(pattern, url)
#
#     root = tk.Tk()
#     root.withdraw()
#
#     save_path = filedialog.asksaveasfilename(
#         defaultextension=".pdf",
#         filetypes=[("PDF files", "*.pdf")],
#         initialfile="placeholder.pdf",
#         title="placeholder"
#     )
#
#     if save_path:
#         if export_to_template(url):
#             html_to_pdf()
#         else:
#             print("Placeholder error")
#     else:
#         print("Save cancelled")
