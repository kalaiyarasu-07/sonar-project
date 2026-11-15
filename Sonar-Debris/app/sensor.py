
import requests
import time

ESP8266_URL = "http://10.206.103.33"

last_processed_cycle = 0


def get_sensor_data():
    """Get the latest live sensor reading."""

    try:
        response = requests.get(
            f"{ESP8266_URL}/data",
            timeout=3
        )
        response.raise_for_status()

        return {
            "connected": True,
            **response.json()
        }

    except requests.RequestException as error:
        return {
            "connected": False,
            "error": str(error)
        }


def get_complete_scan():
    """Retrieve the latest completed scan."""

    try:
        response = requests.get(
            f"{ESP8266_URL}/scan",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if not data.get("complete"):
            return {
                "success": False,
                "error": "Waiting for first completed scan"
            }

        if len(data.get("points", [])) != 91:
            return {
                "success": False,
                "error": "Incomplete scan measurements"
            }

        return {
            "success": True,
            "cycle": data["cycle"],
            "count": data["count"],
            "points": data["points"]
        }

    except (requests.RequestException, ValueError, KeyError) as error:
        return {
            "success": False,
            "error": str(error)
        }


def get_new_scan():
    """Return a scan only when a new cycle is available."""

    global last_processed_cycle

    scan = get_complete_scan()

    if not scan["success"]:
        return scan

    cycle = scan["cycle"]

    if cycle <= last_processed_cycle:
        return {
            "success": True,
            "new_scan": False,
            "cycle": cycle
        }

    last_processed_cycle = cycle

    return {
        **scan,
        "new_scan": True
    }


def wait_for_new_scan():
    """Wait until the ESP8266 completes another scan."""

    while True:
        result = get_new_scan()

        if not result["success"]:
            print("Scanner:", result.get("error"))
        elif result["new_scan"]:
            print(
                f"New scan received: Cycle {result['cycle']} "
                f"| Measurements: {result['count']}"
            )
            return result

        time.sleep(0.5)
