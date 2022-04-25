import sys
import os
import json
import datetime
import requests
import argparse
from stravatools import weeks
from typing import Tuple


def client_credentials() -> Tuple[str, str]:
    credentials_filename = ".client_credentials"
    with open(credentials_filename) as f:
        creds = json.load(f)
    if "client_id" not in creds or "client_secret" not in creds:
        sys.exit("Client credentials file not in expected format")
    return creds["client_id"], creds["client_secret"]


def get_new_token(rt: str) -> dict:
    client_id, client_secret = client_credentials()
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": rt,
    }
    url = "https://www.strava.com/oauth/token"
    print(f"{url}", data)
    r = requests.post(url, data=data)
    print("API Response", r.status_code)
    print(r.text)
    if r.status_code > 299:
        sys.exit("Something went wrong")
    return json.loads(r.text)


def move_file(from_name: str, to_name: str) -> None:
    try:
        os.remove(to_name)
    except OSError:
        pass
    os.rename(from_name, to_name)


def get_auth_token() -> str:
    token_filename = "token.json"
    token_filename_old = "token.old"

    with open(token_filename) as f:
        data = json.load(f)
    if data["expires_at"] > datetime.datetime.now().timestamp():
        print("Using saved token")
        return data["access_token"]

    refresh_token = data["refresh_token"]
    print(f"Need a new token: refresh_token={refresh_token}")
    data = get_new_token(refresh_token)
    move_file(token_filename, token_filename_old)
    with open(token_filename, "w") as outfile:
        json.dump(data, outfile)
    return data["access_token"]


def get_activities(week: int, year: int, force: bool) -> None:
    filename = f"activities/{year}-{week:02d}.json"
    print(filename)
    if not force and os.path.isfile(filename):
        print(f"{filename} already downloaded")
        return
    auth_token = get_auth_token()
    header = {
        "Authorization": f"Bearer {auth_token}"
    }
    start, end = weeks.get_epoch_range(week, year)
    r = requests.get(f"https://www.strava.com/api/v3/athlete/activities?before={end}&after={start}", headers=header)
    print("Status code:", r.status_code)
    if r.status_code == 200:
        with open(filename, "w") as outfile:
            json.dump(json.loads(r.text), outfile)


def main():
    parser = argparse.ArgumentParser(description="Get Strava activities for specified week")
    parser.add_argument("-w", "--week", type=int, default=None, help="week number")
    parser.add_argument("-y", "--year", type=int, default=None, help="year")
    parser.add_argument("-f", "--force", action="store_true", default=False, help="force download, even if file exists")
    args = parser.parse_args()

    if args.year and not args.week:
        parser.error("--year is only valid if --week is specified")

    week, year = weeks.get_week_year(args.week, args.year)
    get_activities(week, year, args.force)


if __name__ == "__main__":
    main()
