
from sensor import get_complete_scan

from reconstruction import (
    convert_scan_to_points,
    get_scan_summary
)

print("SONAR DEBRIS - RECONSTRUCTION ENGINE 2.0")

scan = get_complete_scan()

if not scan["success"]:
    print("Scan error:", scan.get("error"))
    raise SystemExit

points = convert_scan_to_points(
    scan["points"]
)

summary = get_scan_summary(
    scan["points"],
    points
)

print("\nSCAN CYCLE:", scan["cycle"])

print("\nRECONSTRUCTION SUMMARY")

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nFIRST 10 RECONSTRUCTED POINTS")

for point in points[:10]:
    print(point)
