
import math
import statistics


# ==========================================
# CONFIGURATION
# ==========================================

MIN_DISTANCE = 2.0
MAX_DISTANCE = 10.0

MAX_ANGLE_GAP = 6.0
DISTANCE_JUMP_THRESHOLD = 3.0

MIN_CLUSTER_POINTS = 2


# ==========================================
# STEP 1: VALIDATE SENSOR READINGS
# ==========================================

def validate_readings(scan_data):

    valid = []

    for reading in scan_data:

        try:
            angle = float(reading["angle"])
            distance = float(reading["distance"])

        except (KeyError, TypeError, ValueError):
            continue

        if not math.isfinite(angle) or not math.isfinite(distance):
            continue

        if not (0 <= angle <= 180):
            continue

        if not reading.get("detected", False):
            continue

        if not (MIN_DISTANCE <= distance <= MAX_DISTANCE):
            continue

        valid.append({
            "angle": angle,
            "distance": distance
        })

    return sorted(valid, key=lambda p: p["angle"])


# ==========================================
# STEP 2: REMOVE ISOLATED NOISY READINGS
# ==========================================

def filter_noise(readings):

    if len(readings) < 3:
        return readings.copy()

    filtered = []

    for i, point in enumerate(readings):

        neighbors = []

        if i > 0:
            neighbors.append(readings[i - 1]["distance"])

        if i < len(readings) - 1:
            neighbors.append(readings[i + 1]["distance"])

        median_distance = statistics.median(neighbors)

        if abs(
            point["distance"] - median_distance
        ) <= DISTANCE_JUMP_THRESHOLD:

            filtered.append(point)

    return filtered


# ==========================================
# STEP 3: GROUP NEIGHBORING DETECTIONS
# ==========================================

def cluster_points(readings):

    if not readings:
        return []

    clusters = []
    current_cluster = [readings[0]]

    for point in readings[1:]:

        previous = current_cluster[-1]

        angle_gap = (
            point["angle"] - previous["angle"]
        )

        distance_gap = abs(
            point["distance"] - previous["distance"]
        )

        same_region = (
            angle_gap <= MAX_ANGLE_GAP
            and distance_gap <= DISTANCE_JUMP_THRESHOLD
        )

        if same_region:
            current_cluster.append(point)

        else:
            clusters.append(current_cluster)
            current_cluster = [point]

    clusters.append(current_cluster)

    return [
        cluster
        for cluster in clusters
        if len(cluster) >= MIN_CLUSTER_POINTS
    ]


# ==========================================
# STEP 4: POLAR TO CARTESIAN CONVERSION
# ==========================================

def convert_scan_to_points(scan_data):

    valid = validate_readings(scan_data)

    filtered = filter_noise(valid)

    clusters = cluster_points(filtered)

    points = []

    for cluster_id, cluster in enumerate(clusters):

        for reading in cluster:

            angle = reading["angle"]
            distance = reading["distance"]

            radians = math.radians(angle)

            x = distance * math.cos(radians)
            y = distance * math.sin(radians)

            points.append({
                "angle": angle,
                "distance": distance,
                "x": round(x, 3),
                "y": round(y, 3),
                "cluster": cluster_id
            })

    return points


# ==========================================
# STEP 5: ESTIMATE OBJECT DIMENSIONS
# ==========================================

def estimate_dimensions(points):

    if not points:
        return {
            "width": None,
            "height": None,
            "depth": None,
            "estimated_area": None
        }

    x_values = [p["x"] for p in points]
    y_values = [p["y"] for p in points]

    width = max(x_values) - min(x_values)
    height = max(y_values) - min(y_values)

    return {
        "width": round(width, 2),
        "height": round(height, 2),
        "depth": round(
            statistics.median(
                p["distance"] for p in points
            ),
            2
        ),
        "estimated_area": round(width * height, 2)
    }


# ==========================================
# STEP 6: SCAN SUMMARY
# ==========================================

def get_scan_summary(scan_data, detected_points):

    valid_measurements = [
        p for p in scan_data
        if float(p.get("distance", 0)) > 0
    ]

    distances = [
        p["distance"] for p in detected_points
    ]

    dimensions = estimate_dimensions(detected_points)

    return {
        "total_measurements": len(scan_data),

        "valid_measurements": len(valid_measurements),

        "detected_points": len(detected_points),

        "object_regions": len(set(
            p["cluster"] for p in detected_points
        )),

        "minimum_distance": round(min(distances), 2)
            if distances else None,

        "maximum_distance": round(max(distances), 2)
            if distances else None,

        "dimensions": dimensions
    }
