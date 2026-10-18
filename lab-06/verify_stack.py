import argparse
import json
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def get_json(url):
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def verify(expect_alerts):
    health = get_json("http://grafana:3000/api/health")
    if health.get("database") != "ok":
        raise RuntimeError("Grafana database is not ready")

    targets = get_json("http://prometheus:9090/api/v1/targets")["data"]["activeTargets"]
    delivery = [t for t in targets if t["labels"].get("job") == "delivery_service"]
    if not delivery or delivery[0]["health"] != "up":
        raise RuntimeError("Delivery metrics scrape target is not UP yet")

    expressions = [
        "total_deliveries",
        "pending_deliveries",
        "on_the_way_deliveries",
        "average_delivery_time_sum / average_delivery_time_count",
    ]
    values = {}
    for expression in expressions:
        query = urlencode({"query": expression})
        result = get_json(f"http://prometheus:9090/api/v1/query?{query}")
        if result.get("status") != "success" or not result["data"]["result"]:
            raise RuntimeError(f"No query data yet: {expression}")
        values[expression] = result["data"]["result"][0]["value"][1]

    alerts = get_json("http://prometheus:9090/api/v1/alerts")["data"]["alerts"]
    firing = {a["labels"]["alertname"] for a in alerts if a["state"] == "firing"}
    expected = {"HighPendingDeliveries", "HighAverageDeliveryTime"}
    if expect_alerts and not expected.issubset(firing):
        raise RuntimeError(f"Waiting for both demonstration alerts to fire; firing={sorted(firing)}")
    print("Grafana health: OK", flush=True)
    print("Prometheus delivery_service target: UP", flush=True)
    for expression, value in values.items():
        print(f"{expression} = {value}", flush=True)
    print(f"Firing alerts: {sorted(firing)}", flush=True)
    print("Monitoring verification passed.", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-alerts", action="store_true")
    args = parser.parse_args()
    deadline = time.monotonic() + 150
    while True:
        try:
            verify(args.expect_alerts)
            return
        except (URLError, TimeoutError, RuntimeError, KeyError, json.JSONDecodeError) as error:
            if time.monotonic() >= deadline:
                raise
            print(f"Waiting: {error}", flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
