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

def get_grade_name(grade_id):
    return {
        150: "1",
        200: "2",
        320: "3",
        375: "4a",
        400: "4b",
        450: "4c",
        500: "5a",
        600: "5a+",
        700: "5b",
        800: "5b+",
        900: "5c",
        940: "5c+",
        1000: "6a",
        1100: "6a+",
        1200: "6b",
        1300: "6b+",
        1400: "6c",
        1500: "6c+",
        1600: "7a",
        1700: "7a+",
        1800: "7b",
        1900: "7b+",
        2020: "7c",
        2100: "7c+",
        2250: "8a",
        2350: "8a+",
        2400: "8b",
        2520: "8b+",
        2600: "8c",
        2700: "8c+",
        2800: "9a",
        2900: "9a+",
        3100: "9b",
        3200: "9b+",
        3300: "9c",
        # Bouldering  
        9700: "1",
        9770: "2",
        9800: "3",
        9850: "4a",
        9975: "4b",
        10025: "4c",
        10075: "5a",
        10200: "5b",
        10400: "5c",
        10600: "6a",
        10800: "6a+",
        11000: "6b",
        11200: "6b+",
        11400: "6c",
        11600: "6c+",
        11700: "7a",
        11900: "7a+",
        12100: "7b",
        12300: "7b+",
        12500: "7c",
        12700: "7c+",
        12900: "8a",
        13100: "8a+",
        13300: "8b",
        13500: "8b+",
        13700: "8c",
        13900: "8c+",
        14100: "9a"
    }[grade_id]

def get_style_name(style_id):
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
        #Bouldering
        100: "🟢 Flash",
        101: "🟢 Top",
        102: "🔴 Project",
        103: "🟢 Repetition"
    }[style_id]

def get_type_name(route):
    if route['route_type'] == 'SPORT_CLIMBING':
        return {
            0: '[S] Lead',
            1: '[S] Toprope'
        }[route['top_rope']]

    if route['route_type'] == 'MULTI_PITCH':
        return {
            0: '[MP] Leading',
            1: '[MP] Following',
            2: '[MP] Alternate leads'
        }[route['top_rope']]

    if route['route_type'] == 'BOULDER':
        return '[B] Boulder'

    raise Exception()

def get_max_grade(routes, route_type, style_ids):
    return max(map(lambda x: x['grade_id'], filter(lambda y: y['route_type'] == route_type and y['style_id'] in style_ids, routes)), default=None)

def get_title(location):
    return f"🧗 {'Outdoor' if location['location_outdoor'] == 1 else 'Indoor'} climbing / {location['location_name']}"

def get_description(session, routes):
    # Only comment if no route
    if not routes:
        return session['session_comment']
    
    # Main
    description = f"Total ascents: {len(routes):02d}\n"

    climbed_height = sum(map(lambda x: x['ascend_height'], routes))
    if climbed_height > 0.0:
        description += f"Climbed height: {f'{climbed_height:.0f} m'}\n"

    description += f"Most difficult: \n"
    max_sport_climbing_grade = get_max_grade(routes, 'SPORT_CLIMBING', [1, 2, 3, 10])
    if max_sport_climbing_grade:
        description += f" - Sport climbing [S]: {get_grade_name(max_sport_climbing_grade)}\n"
    max_multi_pitch_grade = get_max_grade(routes, 'MULTI_PITCH', [1, 2, 3, 10])
    if max_multi_pitch_grade:
        description += f" - Multi-pitch climbing [MP]: {get_grade_name(max_multi_pitch_grade)}\n"
    max_boulder_grade = get_max_grade(routes, 'BOULDER', [100, 101, 103])
    if max_boulder_grade:
        description += f" - Bouldering [B]: {get_grade_name(max_multi_pitch_grade)}\n"
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
        if route['ascend_height'] > 0.0:
            description += f" | {route['ascend_height']:.0f} m"
        description += "\n"

        description += get_grade_name(route['grade_id'])
        description += f" | {get_style_name(route['style_id'])}"
        description += f" | {get_type_name(route)}\n"

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
        current_time = up_and_down_circle(track_points, location['latitude'], location['longitude'], current_time, time_end, elevation, route['ascend_height'])

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
