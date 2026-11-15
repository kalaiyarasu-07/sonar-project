
from sensor import wait_for_new_scan

print("SONAR DEBRIS - AUTOMATIC SCAN TEST")
print("Waiting for new scan cycles...\n")

while True:
    scan = wait_for_new_scan()

    detected = [
        point for point in scan["points"]
        if point["detected"]
    ]

    print("Cycle:", scan["cycle"])
    print("Total readings:", scan["count"])
    print("Detected points:", len(detected))
    print("Sample:", detected[:5])
    print("-" * 40)

