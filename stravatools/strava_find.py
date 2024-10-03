import argparse
import json
import sys
import webbrowser
from math import asin, cos, radians, sin, sqrt
from statistics import mean

import OSGridConverter as osg
import polyline


def polyline_bounding_box(pl: str, border: float = 0.0):
    """Return the bounding box (latlon) of a polyline."""
    latlon = polyline.decode(pl)
    lats, lons = zip(*latlon)
    return min(lats), min(lons), max(lats), max(lons)


def bb_add_border(bb, border: float):
    """Add a border of `border` km to all sides of bb."""
    lat_border = border * 360 / 40075
    mid_lat = mean([bb[0], bb[2]])
    lon_border = lat_border / cos(radians(mid_lat))
    return bb[0] - lat_border, bb[1] - lon_border, bb[2] + lat_border, bb[3] + lon_border


def bb_add_point(bb, point):
    """Extend bounding box (if necessary) to include point."""
    return min(bb[0], point[0]), min(bb[1], point[1]), max(bb[2], point[0]), max(bb[3], point[1])


def point_in_bounding_box(point, bb):
    """Is point (lat, lon) in bounding box (min lat, min lon, max lat, max lon)"""
    return bb[0] <= point[0] <= bb[2] and bb[1] <= point[1] <= bb[3]


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def bb_compare(pl, point, s, radius, min_rad):
    bounding_box = polyline_bounding_box(pl)
    bounding_box = bb_add_point(bounding_box, s)
    bounding_box = bb_add_border(bounding_box, radius)
    if point_in_bounding_box(point, bounding_box):
        mid_lat = mean([bounding_box[0], bounding_box[2]])
        mid_lon = mean([bounding_box[1], bounding_box[3]])
        d = haversine(*point, mid_lat, mid_lon)
        return True, d
    return False, 0


def start_compare(pl, point, s, radius, min_rad):
    d = haversine(*point, *s)
    proximity = min_rad <= d < radius
    return proximity, d


def all_compare(pl, point, s, radius, min_rad):
    route = polyline.decode(pl)
    d = haversine(*point, *s)
    for r in route:
        distance = haversine(*point, *r)
        if distance < d:
            d = distance
    proximity = min_rad <= d < radius
    return proximity, d


def find(point, radius, files, compare_fn, *, min_rad=0, activity_type=None):
    found = []
    for f in files:
        with open(f) as json_file:
            data = json.load(json_file)
        for act in reversed(data):
            s = act["start_latlng"]
            act_type = act["type"]
            if not s or (activity_type and act_type != activity_type):
                continue
            proximity, d = compare_fn(act["map"]["summary_polyline"], point, s, radius, min_rad)
            if proximity:
                found.append([d, act["id"], act_type, act["name"], act["start_date_local"]])
    return found


def get_latlon(s):
    bits = s.split(",")
    try:
        lat = float(bits[0])
        lon = float(bits[1])
    except ValueError:
        sys.exit("Error: expecting lat lon location in the form '50.203, 0.3241'")
    return lat, lon


def get_latlon_from_grid(s):
    try:
        latlon = osg.grid2latlong(s)
    except (osg.base.OSGridError, TypeError) as error:
        sys.exit(f"Error: Invalid OS grid reference. Expecting something like 'TQ 271 865': {error}")
    return latlon.latitude, latlon.longitude


def main():
    parser = argparse.ArgumentParser(
        description="Find activities near given location (distances in km)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-m", "--min", type=float, default=0.0, help="find activities at least this far from location")
    parser.add_argument("-g", "--grid", action="store_true", default=False, help="use OS Grid Ref")
    parser.add_argument("-r", "--reverse", action="store_true", default=False, help="reverse order of results")
    parser.add_argument("-n", "--number", type=int, default=None, help="show only top 'number' results")
    parser.add_argument("-o", "--open", action="store_true", help="open every (CAREFUL!) returned route in a browser")
    parser.add_argument(
        "--mode",
        type=str,
        default="start",
        choices=["start", "box", "all"],
        help="matching mode",
    )
    parser.add_argument(
        "-d", "--distance", type=float, default=1.0, help="find activities as most this far from location"
    )
    parser.add_argument(
        "-s",
        "--sort",
        type=str,
        choices=["distance", "date"],
        default="distance",
        help="sort results using"
    )
    parser.add_argument(
        "-a",
        "--activity",
        type=str,
        choices=["Run", "Hike", "Bike"],
        default=None,
        help="only show activities of this type",
    )
    parser.add_argument("location", type=str, help="location of interest")
    parser.add_argument("files", nargs="+", help="activity files")
    args = parser.parse_args()

    if args.grid:
        ll = get_latlon_from_grid(args.location)
    else:
        ll = get_latlon(args.location)

    if args.mode == "start":
        compare_fn = start_compare
    elif args.mode == "box":
        compare_fn = bb_compare
    else:
        compare_fn = all_compare

    found = find(ll, args.distance, args.files, compare_fn, min_rad=args.min, activity_type=args.activity)
    if args.sort == "distance":
        found.sort(key=lambda x: x[0], reverse=args.reverse)
    else:
        found.sort(key=lambda x: x[4], reverse=args.reverse)
    for a in found[:args.number]:
        url = f"https://www.strava.com/activities/{a[1]}"
        if args.open:
            webbrowser.open_new(url)
        else:
            print(f"{a[0]:.02f} {url} - {a[2]} - {a[3]} - {a[4]}")


if __name__ == "__main__":
    main()
