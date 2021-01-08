import csv
import sys


def printable_time(s: int) -> str:
    hours = int(s / 3600)
    mins = (s % 3600) / 60
    return f"{hours}:{mins:.0f}"


def main():
    total_distance = 0
    total_training = 0
    total_time = 0

    reader = csv.reader(sys.stdin)
    header = next(reader, None)
    distance_index = header.index("distance")
    elapsed_time_index = header.index("elapsed_time")
    training_index = header.index("training_distance")

    for row in reader:
        total_time += float(row[elapsed_time_index])
        total_distance += float(row[distance_index])
        total_training += float(row[training_index])

    print("Time (HH:MM):", printable_time(total_time))
    print(f"Distance (km): {total_distance/1000:0.1f}")
    print(f"Running equivalent (km): {total_training/1000:0.1f}")


if __name__ == "__main__":
    main()
