# Strava Tools

> **NOTE:** This was written as a quick personal project and never intended to
> be used by anyone but me. This is reflected in some of the design choices,
> lack of error handling, no test cases, etc. If it is of any use to anyone else
> that is a happy accident.

## File Structure

The code is not very configurable (see above) and assumes a certain file
structure. I retrieve and store activities based on the calendar week and store
them in files of the form `YYYY-WW.json`.

`activities/` The directory where all activity files are stored.

`.client_credentials` is a JSON document required to refresh the temporary
token. It should look something like this:
```
{
    "client_id": "12356",
    "client_secret": "123456____________________________123456"
}
```
These credentials can be found on your Strava profile page after you have
created your app.

`token.json` contains the temporary token and refresh code. See [section on the token file](#getting-the-initial-token-file) for more detail.

## The Tools

### strava_get

```
usage: strava_get [-h] [-w WEEK] [-y YEAR] [-f]

Get Strava activities for specified week

optional arguments:
  -h, --help            show this help message and exit
  -w WEEK, --week WEEK  week number
  -y YEAR, --year YEAR  year
  -f, --force           force download, even if file exists
```

Gets all the activities for a given week number in a given year. With no
week/year specified it will get the activities for the previous week (last
completed week). If the activities file already exists, use `-f` to force the
get (otherwise it assumes the data is already there). `strava_get` checks the
validity of the temporary token in `token.json` and requests a new temporary
token if it has expired.

### strava_summary

Probably very specific to me. Creates a simple summary of activities, either
given a week/year (assumes last week if none provided) or a set of files.

```
usage: strava_summary [-h] [-c] [-w WEEK] [-y YEAR] [files [files ...]]

Summarise Strava activities for specified week(s)

positional arguments:
  files                 activity files

optional arguments:
  -h, --help            show this help message and exit
  -c, --csv             CSV format output
  -w WEEK, --week WEEK  week number
  -y YEAR, --year YEAR  year
```

Running with `-c` creates a CSV format (probably most useful).

One of the metrics generated is the "training distance". The training distance
is based on my quirky way of converting everything into running kilometres. I
assume I need to cycle 4km to get the equivalent of 1 running km. Swimming 1km
is equivalent to running 3km. Everything else (hikes, SUPs, kayaking, ...) is
worth 0. I use this to calculate a "running equivalent" training distance. It is
probably pointless, certainly unscientific. I did say I wrote this for me!

### strava_find

Find activities within a radius (specified by `--distance`)of a given `location`.
`location` can be specified with (latitude,longitude) or a UK Ordnance Survey grid reference.

By default `strava_find` will search for activities with a starting point within the specified distance of `location`.
A minimum distance (`--min`) can also be given to search in an annulus around `location`.

The `mode` flag affects the way activities are selected:
* `start` (default): compares `location` and the starting point of the activity
* `box`: search for activities for which `location` is in the bounding box of the activity, extended by `distance`
* `all`: search for activities that have a point on the polyline within `distance` of `location`

`strava_find` has options to change the output sorting order and limit the number of returned results.

```
usage: strava_find [-h] [-m MIN] [-g] [-r] [-n NUMBER]
                   [--mode {start,box,all}] [-d DISTANCE] [-s {distance,date}]
                   [-a {Run,Hike,Bike}]
                   location files [files ...]

Find activities near given location (distances in km)

positional arguments:
  location              location of interest
  files                 activity files

options:
  -h, --help            show this help message and exit
  -m MIN, --min MIN     find activities at least this far from location
                        (default: 0.0)
  -g, --grid            use OS Grid Ref (default: False)
  -r, --reverse         reverse order of results (default: False)
  -n NUMBER, --number NUMBER
                        show only top 'number' results (default: None)
  --mode {start,box,all}
                        matching mode (default: start)
  -d DISTANCE, --distance DISTANCE
                        find activities as most this far from location
                        (default: 1.0)
  -s {distance,date}, --sort {distance,date}
                        sort results using (default: distance)
  -a {Run,Hike,Bike}, --activity {Run,Hike,Bike}
                        only show activities of this type (default: None)
```

### strava_csv_totals

Quick hack to total up some of the numbers generated by `strava_summary -c`. See
below for some examples.

### strava_gridplot

Given a list of files (eg `strava_gridplot activities/2020*`) it will extract
all the valid polylines from the activity files and generate a montage png. The
results looks better than I'd expected!

```
usage: strava_gridplot [-h] [-o OUTPUT] files [files ...]

Plot a montage of Strava activities

positional arguments:
  files                 Activity files

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output filename (default: activities.png)
```

Plotting the long/lat coordinates on a cartesian graph gives a very distorted
map (unless you run on the equator). I take the first latitude measurement of
each activity and scale the `x` coordinates by `cos(lat)`. Scaling by some
average value of latitude over the activity might be slightly better but I don't
think my activities are large enough for that to make any real difference. Feel
free to do something different. See
[this article](http://surferhelp.goldensoftware.com/editmap/using_scaling_to_minimize_distortion_on_latitude_longitude_maps.htm)
for more information about scaling coordinates.

This is a montage of all my 2020 activities, generated with the following command:
```
strava_gridplot activities/2020-*
```
![Example output](docs/activities.png "Output of strava_gridplot")

## Getting the initial token file

The temporary token from your Strava profile page only gives `scope:read`, which
is not sufficient to read your activity data. I went for `scope:activity_all` to
ensure I could retrieve both public and private activities.

The process of getting that first token with the correct permission is described
in the answer here:
[Problem with access token in Strava API v3 GET all athlete activities](https://stackoverflow.com/questions/52880434/problem-with-access-token-in-strava-api-v3-get-all-athlete-activities)

I used the browser for the first two steps, to get the authorization code, then
wrote a simple script to do the third PUT step. I saved the returned JSON into
`token.json`. The file includes the temporary access token as well as the
refresh token required to get a new temporary token after the temporary token
has expired.

The token file looks like this:
```
{
  "token_type": "Bearer",
  "expires_at":i 1609600464,
  "expires_in": 21600,
  "refresh_token": "0c626_____________________________850fdc",
  "access_token": "910d2_____________________________192e85",
  ...
}
```

## Pagination

I haven't implemented pagination. As I get my activities in weekly chunks, I
have never needed it, and probably never will.

## Examples

These are just some examples, to remind me...

Get totals for all Run activities (also works for Ride, etc). Ride picks up both
physical and virtual rides.
```
strava_summary -c activities/* | csvgrep -c 3 -m Run | strava_csv_totals
```

All the Run activities in the 2020 calendar year.
```
strava_summary -c activities/* | csvgrep -c 1 -m "2020-" | csvgrep -c 3 -m Run | strata_csv_totals
```
Because I save activities based on the ISO week number,
`strava_summary -c activities/YYYY*` gives all the activities in the ISO year
(week 1 to week 52 or 53), which will include some days in the previous and/or
following year. Using the above is useful if you want your annual totals to
tally with Strava's statistics.
