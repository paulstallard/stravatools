import argparse
import csv
from decimal import Decimal
import json
import os
import sys
from stravatools import weeks


def pretty_time(s: int) -> str:
    hours = int(s / 3600)
    mins = int((s % 3600) / 60)
    secs = s % 60
    if hours:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def mins_per(average_speed: float, distance: int = 1000) -> str:
    secs = int(round(distance / average_speed))
    return pretty_time(secs)


def simple_show(a: dict) -> None:
    print(a["date"])
    print(f'{a["start_time"]} {a["act_type"]} - {a["name"]}. {pretty_time(a["elapsed_time"])} [{a["speed"]}]')
    print(f'{a["distance"]/Decimal(1000)}')


first_time = True


def csv_show(a: dict) -> None:
    global first_time
    columns = [
        "date",
        "start_time",
        "act_type",
        "name",
        "elapsed_time",
        "average_speed",
        "distance",
        "training_distance",
        "total_elevation_gain"
    ]
    if first_time:
        print(",".join(columns))
        first_time = False
    cw = csv.writer(sys.stdout)
    cw.writerow(str(a[col]) for col in columns)


def extract_data(data: dict) -> dict:
    deets = {
        "name": data["name"],
        "date": data["start_date_local"][:10],
        "start_time": data["start_date_local"][11:16],
        "act_type": data["type"],
        "distance": data["distance"],
        "average_speed": data["average_speed"],
        "elapsed_time": data["moving_time"],
        "total_elevation_gain": data["total_elevation_gain"],
    }
    if deets["act_type"] == "Run":
        deets["speed"] = mins_per(deets["average_speed"], 1000)
        deets["training_distance"] = deets["distance"]
    elif deets["act_type"] == "Swim":
        deets["speed"] = mins_per(deets["average_speed"], 100)
        deets["training_distance"] = deets["distance"] * Decimal(3)
    elif deets["act_type"] in ["Ride", "VirtualRide"]:
        deets["speed"] = f'{float(deets["average_speed"]) * 3.6:.02f}'
        deets["training_distance"] = deets["distance"] / Decimal(4)
    else:
        deets["speed"] = f'{float(deets["average_speed"]) * 3.6:.02f}'
        deets["training_distance"] = 0
    return deets


def summary(filename: str, csv: bool):
    if not os.path.isfile(filename):
        sys.exit(f"{filename} does not exist")
    with open(filename) as json_file:
        data = json.load(json_file, parse_float=Decimal)
        for i in reversed(data):
            activity = extract_data(i)
            if csv:
                csv_show(activity)
            else:
                simple_show(activity)


def main():
    parser = argparse.ArgumentParser(description="Summarise Strava activities for specified week(s)")
    parser.add_argument("-c", "--csv", action="store_true", default=False, help="CSV format output")
    parser.add_argument("-w", "--week", type=int, default=None, help="week number")
    parser.add_argument("-y", "--year", type=int, default=None, help="year")
    parser.add_argument("files", nargs="*", help="activity files")
    args = parser.parse_args()

    if args.year and not args.week:
        parser.error("--year is only valid if --week is specified")

    if args.files:
        for f in args.files:
            summary(f, args.csv)
    else:
        week, year = weeks.get_week_year(args.week, args.year)
        summary(f"activities/{year}-{week:02d}.json", args.csv)


if __name__ == "__main__":
    main()
