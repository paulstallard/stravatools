import csv
import sys
from statistics import mean, median


def fmt_time(s: float) -> str:
    hours = int(s / 3600)
    mins = (s % 3600) / 60
    return f"{hours}:{mins:02.0f}"


def fmt_distance(d: float) -> str:
    return f"{d/1000:.2f}"


def fmt_elevation(d: float) -> str:
    return f"{d:.0f}"


def show_stats(title: str, vals: list, format):
    print(f"{title:14s}:",
          f"{format(sum(vals))}\t",
          f"(min {format(min(vals))},",
          f"max {format(max(vals))},",
          f"mean {format(mean(vals))},",
          f"median {format(median(vals))})"
          )


def main():
    duration = []
    distance = []
    training = []
    unique_dates = set()
    elevation = []

    reader = csv.reader(sys.stdin)
    header = next(reader, None)
    date_index = header.index("date")
    distance_index = header.index("distance")
    elapsed_time_index = header.index("elapsed_time")
    training_index = header.index("training_distance")
    elevation_index = header.index("total_elevation_gain")

    for n, row in enumerate(reader):
        duration.append(float(row[elapsed_time_index]))
        distance.append(float(row[distance_index]))
        training.append(float(row[training_index]))
        elevation.append(float(row[elevation_index]))
        unique_dates.add(row[date_index])

    if unique_dates:
        print(f"{n+1} activities on {len(unique_dates)} days")
        show_stats("Time (hh:mm)", duration, fmt_time)
        show_stats("Elevation (m)", elevation, fmt_elevation)
        show_stats("Distance (km)", distance, fmt_distance)
        show_stats("Training (~km)", training, fmt_distance)


if __name__ == "__main__":
    main()
