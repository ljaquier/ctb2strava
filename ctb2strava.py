from datetime import datetime, timedelta, timezone
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from geopy.distance import geodesic
import requests
from gpx2strava import gpx2strava, utils


def get_new_sessions(ctb, last_export):
    return sorted(filter(lambda x: x['time_start'] > last_export, ctb['sessions']), key=lambda x: x['time_start'])

def get_location(ctb, session):
    return next(filter(lambda x: x['location_id'] == session['location_id'], ctb['locations']), None)

def get_routes(ctb, session):
    return sorted(filter(lambda x: x['session_id'] == session['session_id'], ctb['routes']), key=lambda x: x['ascend_order'])

def get_route_grade_name(route):
    if route['route_type'] == 'SPEED_CLIMBING' and route['speed_type'] == 0:
        return "Std."

    grade = {
        5: {
            "wi-scale": "WI-1"
        },
        10: {
            "wi-scale": "WI-2"
        },
        15: {
            "wi-scale": "WI-3"
        },
        20: {
            "wi-scale": "WI-4"
        },
        25: {
            "wi-scale": "WI-5"
        },
        30: {
            "wi-scale": "WI-6"
        },
        35: {
            "wi-scale": "WI-7"
        },
        40: {
            "wi-scale": "WI-8"
        },
        100: {
            "uiaa": "1",
            "french": "1",
            "yds": "5.0",
            "aus": "10"
        },
        150: {
            "uiaa": "1",
            "french": "1/2",
            "yds": "5.0/5.1",
            "aus": "10/11"
        },
        200: {
            "uiaa": "2",
            "french": "2",
            "yds": "5.1",
            "aus": "11"
        },
        250: {
            "uiaa": "2+",
            "french": "2/3",
            "yds": "5.1/5.2",
            "aus": "11/12"
        },
        275: {
            "uiaa": "3-",
            "french": "2/3",
            "yds": "5.1/5.2",
            "aus": "11/12"
        },
        300: {
            "uiaa": "3",
            "french": "3",
            "yds": "5.2",
            "aus": "12"
        },
        320: {
            "uiaa": "3/3+",
            "french": "3",
            "yds": "5.2",
            "aus": "12"
        },
        350: {
            "uiaa": "3+",
            "french": "3/4a",
            "yds": "5.2/5.3",
            "aus": "12/13"
        },
        365: {
            "uiaa": "3+/4-",
            "french": "3/4a",
            "yds": "5.2/5.3",
            "aus": "12/13"
        },
        375: {
            "uiaa": "4-",
            "french": "4a",
            "yds": "5.3",
            "aus": "13"
        },
        385: {
            "uiaa": "4-/4",
            "french": "4a/4b",
            "yds": "5.3",
            "aus": "13"
        },
        400: {
            "uiaa": "4",
            "french": "4b",
            "yds": "5.3",
            "aus": "13"
        },
        425: {
            "uiaa": "4/4+",
            "french": "4b/4c",
            "yds": "5.3/5.4",
            "aus": "13/14"
        },
        450: {
            "uiaa": "4+",
            "french": "4c",
            "yds": "5.4",
            "aus": "14"
        },
        475: {
            "uiaa": "4+/5-",
            "french": "4c/5a",
            "yds": "5.4/5.5",
            "aus": "14/15"
        },
        500: {
            "uiaa": "5-",
            "french": "5a",
            "yds": "5.5",
            "aus": "14/15"
        },
        550: {
            "uiaa": "5-/5",
            "french": "5a/+",
            "yds": "5.5/5.6",
            "aus": "14/15"
        },
        600: {
            "uiaa": "5",
            "french": "5a+",
            "yds": "5.6",
            "aus": "15"
        },
        650: {
            "uiaa": "5/5+",
            "french": "5a+/5b",
            "yds": "5.6/5.7",
            "aus": "15/16"
        },
        700: {
            "uiaa": "5+",
            "french": "5b",
            "yds": "5.7",
            "aus": "16"
        },
        750: {
            "uiaa": "5+/6-",
            "french": "5b/+",
            "yds": "5.7/5.8",
            "aus": "16/17"
        },
        800: {
            "uiaa": "6-",
            "french": "5b+",
            "yds": "5.8",
            "aus": "17"
        },
        850: {
            "uiaa": "6-/6",
            "french": "5b+/5c",
            "yds": "5.8/5.9",
            "aus": "17/18"
        },
        900: {
            "uiaa": "6",
            "french": "5c",
            "yds": "5.9",
            "aus": "18"
        },
        920: {
            "uiaa": "6",
            "french": "5c/+",
            "yds": "5.9",
            "aus": "18"
        },
        940: {
            "uiaa": "6/6+",
            "french": "5c+",
            "yds": "5.9/5.10a,",
            "aus": "18/19"
        },
        950: {
            "uiaa": "6/6+",
            "french": "5c+/6a",
            "yds": "5.9/5.10a",
            "aus": "18/19"
        },
        1000: {
            "uiaa": "6+",
            "french": "6a",
            "yds": "5.10a",
            "aus": "19"
        },
        1050: {
            "uiaa": "6+/7-",
            "french": "6a/+",
            "yds": "5.10a/5.10b",
            "aus": "19/20"
        },
        1100: {
            "uiaa": "7-",
            "french": "6a+",
            "yds": "5.10b",
            "aus": "20"
        },
        1150: {
            "uiaa": "7-/7",
            "french": "6a+/6b",
            "yds": "5.10b/5.10c",
            "aus": "20/21"
        },
        1200: {
            "uiaa": "7",
            "french": "6b",
            "yds": "5.10c",
            "aus": "21"
        },
        1250: {
            "uiaa": "7/7+",
            "french": "6b/+",
            "yds": "5.10c/5.10d",
            "aus": "21/22"
        },
        1300: {
            "uiaa": "7+",
            "french": "6b+",
            "yds": "5.10d",
            "aus": "22"
        },
        1350: {
            "uiaa": "7+",
            "french": "6b+/6c",
            "yds": "5.10d/5.11a",
            "aus": "22"
        },
        1400: {
            "uiaa": "7+/8-",
            "french": "6c",
            "yds": "5.11a",
            "aus": "22/23"
        },
        1450: {
            "uiaa": "7+/8-",
            "french": "6c/+",
            "yds": "5.11a/5.11b",
            "aus": "22/23"
        },
        1500: {
            "uiaa": "8-",
            "french": "6c+",
            "yds": "5.11b",
            "aus": "23"
        },
        1550: {
            "uiaa": "8-/8",
            "french": "6c+/7a",
            "yds": "5.11b/5.11c",
            "aus": "23/24"
        },
        1600: {
            "uiaa": "8",
            "french": "7a",
            "yds": "5.11c",
            "aus": "24"
        },
        1650: {
            "uiaa": "8/8+",
            "french": "7a/+",
            "yds": "5.11c/5.11d",
            "aus": "24/25"
        },
        1700: {
            "uiaa": "8+",
            "french": "7a+",
            "yds": "5.11d",
            "aus": "25"
        },
        1750: {
            "uiaa": "8+",
            "french": "7a+/7b",
            "yds": "5.11d/5.12a",
            "aus": "25"
        },
        1800: {
            "uiaa": "8+/9-",
            "french": "7b",
            "yds": "5.12a",
            "aus": "25/26"
        },
        1850: {
            "uiaa": "8+/9-",
            "french": "7b/+",
            "yds": "5.12a/5.12b",
            "aus": "25/26"
        },
        1900: {
            "uiaa": "9-",
            "french": "7b+",
            "yds": "5.12b",
            "aus": "26"
        },
        1950: {
            "uiaa": "9-/9",
            "french": "7b+/7c",
            "yds": "5.12b/5.12c",
            "aus": "26/27"
        },
        2000: {
            "uiaa": "9",
            "french": "7c",
            "yds": "5.12c",
            "aus": "27"
        },
        2020: {
            "uiaa": "9",
            "french": "7c",
            "yds": "5.12c",
            "aus": "27/28"
        },
        2050: {
            "uiaa": "9/9+",
            "french": "7c/+",
            "yds": "5.12c/5.12d",
            "aus": "28"
        },
        2100: {
            "uiaa": "9+",
            "french": "7c+",
            "yds": "5.12d",
            "aus": "28/29"
        },
        2150: {
            "uiaa": "9+",
            "french": "7c+/8a",
            "yds": "5.12d/5.13a",
            "aus": "29"
        },
        2200: {
            "uiaa": "9+/10-",
            "french": "8a",
            "yds": "5.13a",
            "aus": "29/30"
        },
        2250: {
            "uiaa": "9+/10-",
            "french": "8a",
            "yds": "5.13a/5.13b",
            "aus": "29/30"
        },
        2300: {
            "uiaa": "10-",
            "french": "8a/+",
            "yds": "5.13b",
            "aus": "30"
        },
        2325: {
            "uiaa": "10-",
            "french": "8a/+",
            "yds": "5.13b/5.13c",
            "aus": "30"
        },
        2350: {
            "uiaa": "10-/10",
            "french": "8a+",
            "yds": "5.13c",
            "aus": "30/31"
        },
        2375: {
            "uiaa": "10-/10",
            "french": "8a+/8b",
            "yds": "5.13c/5.13d",
            "aus": "30/31"
        },
        2400: {
            "uiaa": "10",
            "french": "8b",
            "yds": "5.13d",
            "aus": "31"
        },
        2450: {
            "uiaa": "10/10+",
            "french": "8b/+",
            "yds": "5.13d/5.14a",
            "aus": "31/32"
        },
        2500: {
            "uiaa": "10+",
            "french": "8b+",
            "yds": "5.14a",
            "aus": "32"
        },
        2520: {
            "uiaa": "10+",
            "french": "8b+",
            "yds": "5.14a",
            "aus": "32/33"
        },
        2550: {
            "uiaa": "10+/11-",
            "french": "8b+/8c",
            "yds": "5.14a/5.14b",
            "aus": "33"
        },
        2600: {
            "uiaa": "11-",
            "french": "8c",
            "yds": "5.14b",
            "aus": "33/34"
        },
        2650: {
            "uiaa": "11-",
            "french": "8c/+",
            "yds": "5.14b/5.14c",
            "aus": "34"
        },
        2700: {
            "uiaa": "11-/11",
            "french": "8c+",
            "yds": "5.14c",
            "aus": "34/35"
        },
        2750: {
            "uiaa": "11-/11",
            "french": "8c+/9a",
            "yds": "5.14c/5.14d",
            "aus": "34/35"
        },
        2800: {
            "uiaa": "11",
            "french": "9a",
            "yds": "5.14d",
            "aus": "35"
        },
        2850: {
            "uiaa": "11",
            "french": "9a/+",
            "yds": "5.14d/5.15a",
            "aus": "35"
        },
        2900: {
            "uiaa": "11/11+",
            "french": "9a+",
            "yds": "5.15a",
            "aus": "35/36"
        },
        3000: {
            "uiaa": "11+",
            "french": "9a+/9b",
            "yds": "5.15a/5.15b",
            "aus": "36"
        },
        3050: {
            "uiaa": "11+/12-",
            "french": "9a+/9b",
            "yds": "5.15a/5.15b",
            "aus": "36/37"
        },
        3100: {
            "uiaa": "12-",
            "french": "9b",
            "yds": "5.15b",
            "aus": "37"
        },
        3150: {
            "uiaa": "12-/12",
            "french": "9b/+",
            "yds": "5.15b/5.15c",
            "aus": "37/38"
        },
        3200: {
            "uiaa": "12",
            "french": "9b+",
            "yds": "5.15c",
            "aus": "38"
        },
        3250: {
            "uiaa": "12/12+",
            "french": "9b+/9c",
            "yds": "5.15c/5.15d",
            "aus": "38/39"
        },
        3300: {
            "uiaa": "12+",
            "french": "9c",
            "yds": "5.15d",
            "aus": "39"
        },
        9700: {
            "v-scale": "VB-",
            "fontainebleau": "1"
        },
        9750: {
            "v-scale": "VB-",
            "fontainebleau": "2"
        },
        9770: {
            "v-scale": "VB-/VB",
            "fontainebleau": "2"
        },
        9800: {
            "v-scale": "VB",
            "fontainebleau": "3"
        },
        9830: {
            "v-scale": "VB",
            "fontainebleau": "3/4a"
        },
        9850: {
            "v-scale": "VB/V0-",
            "fontainebleau": "4a"
        },
        9950: {
            "v-scale": "V0-",
            "fontainebleau": "4a/4b"
        },
        9975: {
            "v-scale": "V0-/V0",
            "fontainebleau": "4b"
        },
        10000: {
            "v-scale": "V0",
            "fontainebleau": "4b/4c"
        },
        10025: {
            "v-scale": "V0/V0+",
            "fontainebleau": "4c"
        },
        10050: {
            "v-scale": "V0+",
            "fontainebleau": "4c/5a"
        },
        10075: {
            "v-scale": "V0+/V1",
            "fontainebleau": "5a"
        },
        10150: {
            "v-scale": "V0+/V1",
            "fontainebleau": "5a/5b"
        },
        10200: {
            "v-scale": "V1",
            "fontainebleau": "5b"
        },
        10300: {
            "v-scale": "V1/V2",
            "fontainebleau": "5b/5c"
        },
        10400: {
            "v-scale": "V2",
            "fontainebleau": "5c"
        },
        10500: {
            "v-scale": "V2/V3",
            "fontainebleau": "5+/6a"
        },
        10600: {
            "v-scale": "V3",
            "fontainebleau": "6a"
        },
        10700: {
            "v-scale": "V3",
            "fontainebleau": "6a/6a+"
        },
        10800: {
            "v-scale": "V3",
            "fontainebleau": "6a+"
        },
        10900: {
            "v-scale": "V3/V4",
            "fontainebleau": "6a+/6b"
        },
        11000: {
            "v-scale": "V3/V4",
            "fontainebleau": "6b"
        },
        11100: {
            "v-scale": "V4",
            "fontainebleau": "6b/6b+"
        },
        11200: {
            "v-scale": "V4",
            "fontainebleau": "6b+"
        },
        11300: {
            "v-scale": "V4/V5",
            "fontainebleau": "6b+/6c"
        },
        11400: {
            "v-scale": "V5",
            "fontainebleau": "6c"
        },
        11500: {
            "v-scale": "V5",
            "fontainebleau": "6c/6c+"
        },
        11600: {
            "v-scale": "V5/V6",
            "fontainebleau": "6c+"
        },
        11650: {
            "v-scale": "V5/V6",
            "fontainebleau": "6c+/7a"
        },
        11700: {
            "v-scale": "V6",
            "fontainebleau": "7a"
        },
        11800: {
            "v-scale": "V6/V7",
            "fontainebleau": "7a/7a+"
        },
        11900: {
            "v-scale": "V7",
            "fontainebleau": "7a+"
        },
        12000: {
            "v-scale": "V7/V8",
            "fontainebleau": "7a+/7b"
        },
        12100: {
            "v-scale": "V8",
            "fontainebleau": "7b"
        },
        12200: {
            "v-scale": "V8",
            "fontainebleau": "7b/7b+"
        },
        12300: {
            "v-scale": "V8",
            "fontainebleau": "7b+"
        },
        12400: {
            "v-scale": "V8/V9",
            "fontainebleau": "7b+/7c"
        },
        12500: {
            "v-scale": "V9",
            "fontainebleau": "7c"
        },
        12600: {
            "v-scale": "V9/V10",
            "fontainebleau": "7c/7c+"
        },
        12700: {
            "v-scale": "V10",
            "fontainebleau": "7c+"
        },
        12800: {
            "v-scale": "V10/V11",
            "fontainebleau": "7c+/8a"
        },
        12900: {
            "v-scale": "V11",
            "fontainebleau": "8a"
        },
        13000: {
            "v-scale": "V11/V12",
            "fontainebleau": "8a/8a+"
        },
        13100: {
            "v-scale": "V12",
            "fontainebleau": "8a+"
        },
        13200: {
            "v-scale": "V12/V13",
            "fontainebleau": "8a+/8b"
        },
        13300: {
            "v-scale": "V13",
            "fontainebleau": "8b"
        },
        13400: {
            "v-scale": "V13/V14",
            "fontainebleau": "8b/8b+"
        },
        13500: {
            "v-scale": "V14",
            "fontainebleau": "8b+"
        },
        13600: {
            "v-scale": "V14/V15",
            "fontainebleau": "8b+/8c"
        },
        13700: {
            "v-scale": "V15",
            "fontainebleau": "8c"
        },
        13800: {
            "v-scale": "V15/V16",
            "fontainebleau": "8c/8c+"
        },
        13900: {
            "v-scale": "V16",
            "fontainebleau": "8c+"
        },
        14000: {
            "v-scale": "V16/V17",
            "fontainebleau": "8c+/9a"
        },
        14100: {
            "v-scale": "V17",
            "fontainebleau": "9a"
        }
    }[route['grade_id']]

    if route['original_grade_system']:
        return grade[route['original_grade_system'].lower()]

    if 'wi-scale' in grade:
        return grade['wi-scale']
    if 'french' in grade:
        return grade['french']
    if 'fontainebleau' in grade:
        return grade['fontainebleau']

    raise Exception()

def get_route_style_name(route):
    if route['route_type'] == 'SPEED_CLIMBING':
        return f"🟢 {route['speed_time']/1000:.2f} s"

    return {
        1: "🟢 Onsight",
        2: "🟢 Flash",
        3: "🟢 Redpoint",
        4: "🟡 a.f",
        5: "🟡 Hangdogging",
        6: "🔴 3/4",
        7: "🔴 1/2",
        8: "🔴 1/4",
        9: "🟡 Aid",
        10: "🟢 Repetition",
        100: "🟢 Flash",
        101: "🟢 Top",
        102: "🔴 Project",
        103: "🟢 Repetition"
    }[route['style_id']]

def get_route_type_name(route):
    if route['route_type'] == 'SPORT_CLIMBING':
        return {
            0: '[S] Lead',
            1: '[S] Toprope'
        }[route['top_rope']]

    if route['route_type'] == 'BOULDER':
        return '[B] Boulder'

    if route['route_type'] == 'SPEED_CLIMBING':
        if route['speed_type'] == 0:
            return '[SPEED] Competition'
        return {
            0: '[SPEED] Lead',
            1: '[SPEED] Toprope'
        }[route['top_rope']]

    if route['route_type'] == 'MULTI_PITCH':
        return {
            0: '[MP] Leading',
            1: '[MP] Following',
            2: '[MP] Alternate leads'
        }[route['top_rope']]

    if route['route_type'] == 'TRAD_CLIMBING':
        return {
            0: '[T] Lead',
            1: '[T] Toprope'
        }[route['top_rope']]

    if route['route_type'] == 'ICE_CLIMBING':
        return {
            0: '[ICE] Lead',
            1: '[ICE] Toprope'
        }[route['top_rope']]

    if route['route_type'] == 'DEEP_WATER_SOLO':
        return '[DWS] No rope'

    if route['route_type'] == 'FREE_SOLO':
        return '[FREE] No rope'

    raise Exception()

def get_route_height(route):
    coefficient = {
        6: 0.75,
        7: 0.5,
        8: 0.25,
    }.get(route['style_id'], 1)
    return round(route['ascend_height']*coefficient)

def get_best_route(routes, route_type, style_ids):
    if route_type == 'SPEED_CLIMBING':
        return min(filter(lambda y: y['route_type'] == route_type, routes), key=lambda x: x['speed_time'], default=None)

    return max(filter(lambda y: y['route_type'] == route_type and y['style_id'] in style_ids, routes), key=lambda x: x['grade_id'], default=None)

def get_title(location):
    return f"🧗 {'Outdoor' if location['location_outdoor'] == 1 else 'Indoor'} climbing / {location['location_name']}"

def get_best_route_line(routes, route_type, clean_style_ids = None, dirty_style_ids = None):
    best_route_clean = get_best_route(routes, route_type, clean_style_ids)
    best_route_dirty = None
    if dirty_style_ids:
        best_route_dirty = get_best_route(routes, route_type, dirty_style_ids)
        if best_route_clean and best_route_dirty and best_route_dirty['grade_id'] <= best_route_clean['grade_id']:
            best_route_dirty = None

    line = ""
    if best_route_clean or best_route_dirty:
        line += " - "
        line += {
            'SPORT_CLIMBING': "Sport climbing [S]",
            'BOULDER': "Bouldering [B]",
            'SPEED_CLIMBING': "Speed climbing [SPEED]",
            'MULTI_PITCH': "Multi-pitch climbing [MP]",
            'TRAD_CLIMBING': "Trad climbing [T]",
            'ICE_CLIMBING': "Ice climbing [ICE]",
            'DEEP_WATER_SOLO': "Deep water soloing [DWS]",
            'FREE_SOLO': "Free soloing [FREE]"
        }[route_type]
        line += ":"

        if best_route_clean:
            line += f" {get_route_grade_name(best_route_clean)}"
        if best_route_dirty:
            line += f" ({get_route_grade_name(best_route_dirty)})"

        line += "\n"

    return line

def get_description(session, routes):
    # Only comment if no route
    if not routes:
        return session['session_comment']
    
    # Main
    description = f"Total ascents: {len(routes):02d}\n"

    climbed_height = sum(map(get_route_height, routes))
    if climbed_height > 0:
        description += f"Climbed height: {f'{climbed_height} m'}\n"

    # Best ascent
    description += f"Best ascent: \n"
    description += get_best_route_line(routes, 'SPORT_CLIMBING', [1, 2, 3, 10], [4, 5, 9])
    description += get_best_route_line(routes, 'BOULDER', [100, 101, 103])
    description += get_best_route_line(routes, 'SPEED_CLIMBING')
    description += get_best_route_line(routes, 'MULTI_PITCH', [1, 2, 3, 10], [4, 5, 9])
    description += get_best_route_line(routes, 'TRAD_CLIMBING', [1, 2, 3, 10], [4, 5, 9])
    description += get_best_route_line(routes, 'ICE_CLIMBING', [1, 2, 3, 10], [4, 5, 9])
    description += get_best_route_line(routes, 'DEEP_WATER_SOLO', [1, 2, 3, 10], [4, 5, 9])
    description += get_best_route_line(routes, 'FREE_SOLO', [1, 2, 3, 10], [4, 5, 9])
    description += "\n"

    # Comment
    if session['session_comment']:
        description += f"{session['session_comment']}\n\n"

    # Routes
    route_number = 1
    for route in routes:
        description += f"{route_number:02d}"
        if route['route_name']:
            description += f" | {route['route_name']}"
        route_height = get_route_height(route)
        if route_height > 0:
            description += f" | {route_height} m"
        description += "\n"

        description += get_route_grade_name(route)
        description += f" | {get_route_style_name(route)}"
        description += f" | {get_route_type_name(route)}\n"

        if route['comment']:
            description += f"{route['comment']}\n"
        
        description += "\n"
        route_number += 1

    return description.strip()

def arc(track_points, center_lat, center_lon, start_angle, stop_angle, current_time, time_end, get_elevation):
    for angle in range(start_angle, stop_angle):
        destination = geodesic(meters=25).destination((center_lat, center_lon), angle)
        track_points.append(
            gpx2strava.TrackPoint(
                destination.latitude,
                destination.longitude,
                get_elevation(angle),
                current_time
            )
        )
        current_time += timedelta(seconds=1)
        if (current_time > time_end):
            return None
    return current_time

def circle(track_points, center_lat, center_lon, current_time, time_end, elevation):
    return arc(track_points, center_lat, center_lon, 0, 360, current_time, time_end, lambda angle: elevation)

def up_and_down_circle(track_points, center_lat, center_lon, current_time, time_end, start_elevation, elevation_amplitude):
    current_time = arc(track_points, center_lat, center_lon, 0, 90, current_time, time_end, lambda angle: start_elevation)
    current_time = arc(track_points, center_lat, center_lon, 90, 180, current_time, time_end, lambda angle: start_elevation + elevation_amplitude * (angle-90)/90)
    current_time = arc(track_points, center_lat, center_lon, 180, 270, current_time, time_end, lambda angle: start_elevation + elevation_amplitude)
    current_time = arc(track_points, center_lat, center_lon, 270, 360, current_time, time_end, lambda angle: start_elevation + elevation_amplitude - elevation_amplitude * (angle-270)/90)
    return current_time

def get_elevation(lat, lon):
   base_url = 'https://api.opentopodata.org/v1'
   params = {'locations': f'{lat},{lon}'}
   elevation = requests.get(f'{base_url}/eudem25m', params=params).json()['results'][0]['elevation']
   if elevation:
       return elevation
   return requests.get(f'{base_url}/mapzen', params=params).json()['results'][0]['elevation']

def get_gpx(session):
    location = get_location(ctb, session)
    routes = get_routes(ctb, session)

    zone_info = ZoneInfo(TimezoneFinder().timezone_at(lat=location['latitude'], lng=location['longitude']))
    current_time = datetime.fromisoformat(session['time_start']).replace(tzinfo=zone_info).astimezone(timezone.utc)
    time_end = datetime.fromisoformat(session['time_end']).replace(tzinfo=zone_info).astimezone(timezone.utc)
    elevation = get_elevation(location['latitude'], location['longitude'])

    track_points = []

    for route in routes:
        current_time = up_and_down_circle(track_points, location['latitude'], location['longitude'], current_time, time_end, elevation, get_route_height(route))

    while current_time:
        current_time = circle(track_points, location['latitude'], location['longitude'], current_time, time_end, elevation)

    return gpx2strava.get_gpx(
        get_title(location),
        get_description(session, routes),
        'RockClimbing',
        track_points
    )


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Create activities on Strava from a Climbing Tracker backups')
    parser.add_argument('config_file', nargs='?', help='Config file')
    parser.add_argument('ctb_file', nargs='?', help='Climbing Tracker backup file')

    args = parser.parse_args()
    if args.config_file and args.ctb_file:
        config = utils.load_json(args.config_file)

        ctb = utils.load_json(args.ctb_file)
        sessions = get_new_sessions(ctb, config['last_export'])
        if not sessions:
            print("No session found")
            sys.exit()

        access_token = gpx2strava.get_access_token(config)
        for session in sessions:
            response = gpx2strava.upload_to_strava(access_token, get_gpx(session))
            print(f"{args.ctb_file} : {response.status_code} : {response.text}")
        
        config['last_export'] = sessions[-1]['time_start']
        utils.save_json(args.config_file, config)
    else:
        parser.print_help()
