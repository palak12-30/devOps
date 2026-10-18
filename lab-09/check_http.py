import time
from urllib.error import URLError
from urllib.request import urlopen


def main():
    for attempt in range(30):
        try:
            with urlopen("http://127.0.0.1:5000/", timeout=2) as response:
                body = response.read().decode("utf-8")
                if response.status != 200 or body != "Hello, Jenkins Multi-Stage Pipeline!":
                    raise RuntimeError(f"Unexpected HTTP response: {response.status} {body!r}")
            print(f"HTTP 200: {body}")
            return
        except (URLError, TimeoutError):
            if attempt == 29:
                raise
            time.sleep(1)


if __name__ == "__main__":
    main()
