import os
import sys
import json
import polyline
import argparse
import math
import matplotlib.pyplot as plt
from typing import List, Tuple


def get_polylines(filename: str) -> List[str]:
    # Return a list of all non-empty polylines in filename
    if not os.path.isfile(filename):
        sys.exit(f"{filename} does not exist")
    with open(filename) as json_file:
        data = json.load(json_file)
    data.sort(key=lambda x: x["start_date"])
    return [
        act["map"]["summary_polyline"]
        for act in data
        if "map" in act and "summary_polyline" in act["map"] and act["map"]["summary_polyline"]
    ]


def transform(ll_pairs: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    # Calc correction factor to scale the x coordinates
    # (based on the activity's first point)
    correction = math.cos(math.radians(ll_pairs[0][0]))
    return [(x*correction, y) for y, x in ll_pairs]


def coords_from_plotline(pl: str) -> Tuple[List, List]:
    # Takes a polyline and returns two lists (x, y) of coordinates
    if not pl:
        sys.exit("Expecting a valid polyline")
    decoded = polyline.decode(pl)
    x, y = map(list, zip(*transform(decoded)))
    return x, y


def gridplot(pls: list, output_filename: str) -> None:
    num_plots = len(pls)

    # Find a reasonable grid for the number of plots
    aspect_ratio = 16 / 9  # 1/math.sqrt(2)
    width = int(math.ceil(math.sqrt(num_plots * aspect_ratio)))
    height = int(math.ceil(num_plots / width))
    if (width - 1) * height >= num_plots:
        width -= 1
    print(f"Plotting {num_plots} maps on a {width}x{height} grid")

    dpi = 300
    plt.style.use("dark_background")
    fig, ax = plt.subplots(height, width, squeeze=False)
    fig.set_size_inches(1920 / dpi, 1080 / dpi)

    for r in range(height):
        for c in range(width):
            if pls:
                x, y = coords_from_plotline(pls.pop(0))
                ax[r, c].plot(x, y, linewidth=0.3)
                # ax[r, c].plot(x, y, linewidth=0.3, marker="o", markersize=.8)
                ax[r, c].axis("equal")
            ax[r, c].axis("off")
    plt.subplots_adjust(hspace=0, wspace=0)
    plt.savefig(output_filename, bbox_inches="tight", pad_inches=0, dpi=1.5 * dpi)


def main():
    parser = argparse.ArgumentParser(
        description="Plot a montage of Strava activities", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("files", nargs="+", help="Activity files")
    parser.add_argument("-o", "--output", type=str, default="activities.png", help="output filename")
    args = parser.parse_args()

    polylines = []
    for f in args.files:
        polylines += get_polylines(f)

    gridplot(polylines, args.output)


if __name__ == "__main__":
    main()
