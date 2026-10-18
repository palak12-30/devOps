import os
import random
import time

from prometheus_client import Gauge, Summary, start_http_server

total_deliveries = Gauge("total_deliveries", "Total number of deliveries")
pending_deliveries = Gauge("pending_deliveries", "Number of pending deliveries")
on_the_way_deliveries = Gauge("on_the_way_deliveries", "Number of deliveries on the way")
average_delivery_time = Summary("average_delivery_time", "Delivery time observations in seconds")


def simulate_delivery(alert_demo=False):
    pending = random.randint(50, 100) if alert_demo else random.randint(10, 20)
    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)
    duration = random.uniform(35, 45) if alert_demo else random.uniform(15, 45)
    total = pending + on_the_way + delivered
    total_deliveries.set(total)
    pending_deliveries.set(pending)
    on_the_way_deliveries.set(on_the_way)
    average_delivery_time.observe(duration)
    print(f"Total={total} Pending={pending} On-the-way={on_the_way} Delivery-time={duration:.2f}s", flush=True)


if __name__ == "__main__":
    alert_demo = os.environ.get("ALERT_DEMO", "false").lower() == "true"
    start_http_server(8000, addr="0.0.0.0")
    print(f"Metrics listening on port 8000; alert demonstration={alert_demo}", flush=True)
    while True:
        simulate_delivery(alert_demo)
        time.sleep(1)
