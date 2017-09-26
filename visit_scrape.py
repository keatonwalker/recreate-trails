import json
from bs4 import BeautifulSoup, element
import requests
import csv
from datetime import datetime
import re
import random
import time

COORD_MATCHER = re.compile(r'\d{2}\.\d+, ?-\d{3}\.\d+')


def _get_soup_page(url):
    r = requests.get(url)
    r.raise_for_status()
    page = None
    try:
        page = BeautifulSoup(r.content, 'html.parser')
    except:
        print "Error: Response could not be parsed."

    return page


def get_visitpage_record(url):
    page_fields = {
        'Overview:': 'overview',
        'Start:': 'start_desc',
        'Distance:': 'distance_desc',
        'Difficulty:': 'difficulty_desc',
        'Maps:': 'maps',
        'Trailhead GPS:': 'gps'
    }
    record = {
        'name': '',
        'overview': '',
        'start_desc': '',
        'distance_desc': '',
        'difficulty_desc': '',
        'maps': '',
        'gps': '',
        'trailhead_lat': '',
        'traihead_long': '',
        'difficulty': '',
        'visit_url': ''
    }
    page = _get_soup_page(url)

    h1_tags = page.find_all('h1')
    for h in h1_tags:
        for child in h.descendants:
            if type(child) == element.NavigableString:
                record['name'] = unicode(child).strip()

    p_tags = page.find_all('p')
    search_strings = page_fields.keys()
    for p in p_tags:
        for child in p.descendants:
            string = ""
            if type(child) == element.NavigableString:
                string = unicode(child)
                if string.strip() in search_strings:
                    record[page_fields[string.strip()]] = p.get_text().replace(string, '').strip()
                elif 'GPS' in string.upper() and record['gps'] == '':
                    record['gps'] = p.get_text().replace(string, '').strip()

            elif type(child) != element.NavigableString and child.get_text() is not None:
                if child.get_text() == 'Overview:':
                    pass

    difficulty_description = record['difficulty_desc']
    if len(difficulty_description.split(',')) > 1:
        record['difficulty'] = difficulty_description.split(',')[0].lower().strip()

    record['trailhead_lat'] = '' if record['gps'] == '' else record['gps'].split(',')[0].strip()
    record['traihead_long'] = '' if record['gps'] == '' else record['gps'].split(',')[1].strip()

    record['visit_url'] = url

    return record



def get_visitpage_gps(url):
    visit_url = url
    # payload = {
    #     'perdiemSearchVO.year': '2017',
    #     'resultName': 'getPerdiemRatesBySearchVO',
    #     'currentCategory.categoryId': '100120',
    #     'perdiemSearchVO.state': state.lower(),
    #     'perdiemSearchVO.city': city.lower(),
    #     'perdiemSearchVO.zip': zipcode
    # }

    r = requests.get(visit_url)
    # r = requests.get(apiCheck_Url.format("270 E Center", "84042"), params=payload)
    # request_time = r.elapsed
    # geocode_time = r.headers['X-Elapsed-Time']
    # print 'Request time', request_time
    # print r.geturl()
    # print r.info()
    page = None
    points = set([])
    try:
        page = BeautifulSoup(r.content, 'html.parser')
    except:
        print "Error: Service did not respond."

    p_tags = page.find_all('p')
    for p in p_tags:
        for child in p.descendants:
            string = ""
            if type(child) != element.NavigableString:
                string = unicode(child)
            elif type(child) != element.NavigableString and child.get_text() is not None:
                string = child.get_text()
                # gps_matches = COORD_MATCHER.findall(child.get_text())
                # if len(gps_matches) > 0:
                #     points.update(gps_matches)
                # else:
                #     print '000'
            gps_matches = COORD_MATCHER.findall(string)
            if len(gps_matches) > 0:
                points.update(gps_matches)
    return points


def scrape_gps_points():
    data = 'VisitUtahLinks.csv'
    out_csv = 'visit_utah_parsed.csv'
    out_rows = [['name', 'location', 'signature', 'outerspacia', 'url', 'lat', 'long']]
    with open(out_csv, 'wb') as out:
        writer = csv.writer(out)
        writer.writerow(out_rows[-1])

    has_points_count = 0
    with open(data, 'rb') as stays:
        reader = csv.DictReader(stays)
        i = 2
        for row in reader:
            url = row['URL']
            time.sleep(random.uniform(2.0, 5.0))
            gps_coord_pairs = list(get_visitpage_gps(url))
            out_point = ['', '']
            if len(gps_coord_pairs) > 0:
                out_point = gps_coord_pairs[0].split(',')
                has_points_count += 1

            out_rows.append([row['Trail Name'],
                             row['Location '],
                             'yes' if row['Signature Trail?'].strip() != '' else 'no',
                             'yes' if row['OuterSpacial?'].strip() != '' else 'no',
                             url,
                             out_point[0].strip(),
                             out_point[1].strip()])
            with open(out_csv, 'ab') as out:
                writer = csv.writer(out)
                writer.writerow(out_rows[-1])
            i += 1
    print 'pages with points:', has_points_count


def create_visit_table():
    url_table = r''
    with open(data, 'rb') as stays:
        reader = csv.DictReader(stays)


if __name__ == '__main__':
    route_urls = {
        'Cable Mountain': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/outdoor-experiences/strenuous/cable-mountain-trail/',
        'Chinle': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/outdoor-experiences/moderate/chinle-trail/',
        'East Rim': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/outdoor-experiences/strenuous/east-rim-trail/',
        'Hidden Canyon': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/adventure-guide/hidden-canyon/',
        'Northgate Peaks': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/outdoor-experiences/easy/northgate-peaks-trail/',
        'Parus Trail (zions)': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/family-guide/parus-trail/',
        'Taylor Creek': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/family-guide/taylor-creek/',
        'Watchman': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/family-guide/watchman/',
        'Weeping Rock': 'https://www.visitutah.com/places-to-go/most-visited-parks/zion/family-guide/weeping-rock/',
        'Wildcat Canyon': 'https://www.visitutah.com/places-to-go/most-visited-parks/monument-valley-tribal-park/wildcat-trail/'
    }
    for route in route_urls:
        print route
        vist_record = get_visitpage_record(route_urls[route])
        time.sleep(0.1)
        with open('data/json/' + route + '.json', 'w') as f_out:
            f_out.write(json.dumps(vist_record, sort_keys=True, indent=4))
