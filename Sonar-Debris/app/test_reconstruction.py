
from sensor import wait_for_new_scan
from reconstruction import (
    convert_scan_to_points,
    get_scan_summary
)
from visualization import create_scan_figure

print("SONAR DEBRIS - 2D RECONSTRUCTION")

while True:

    scan = wait_for_new_scan()

    points = convert_scan_to_points(scan["points"])

    summary = get_scan_summary(
        scan["points"],
        points
    )

    print("\nCycle:", scan["cycle"])
    print("Summary:", summary)

    figure = create_scan_figure(
        points,
        scan["cycle"]
    )

    figure.show()
