import time

import docker

IMAGE = "flask-apparmor:lab05"
PROFILE = "my-apparmor-profile"


def main():
    client = docker.from_env()
    container = None
    try:
        print(f"Using the existing local image: {IMAGE}")
        client.images.get(IMAGE)
        container = client.containers.run(
            IMAGE, security_opt=[f"apparmor={PROFILE}"], detach=True
        )
        print(f"Container started: {container.short_id}")
        container.reload()
        print(f"Requested security options: {container.attrs['HostConfig']['SecurityOpt']}")
        actual_profile = container.attrs["AppArmorProfile"]
        print(f"Configured AppArmor profile: {actual_profile}")
        if actual_profile != PROFILE:
            raise RuntimeError("The expected AppArmor profile was not applied")

        code, output = container.exec_run(
            ["python", "-c", "from pathlib import Path; print(Path('/proc/self/attr/current').read_text())"]
        )
        active_label = output.decode().strip()
        print(f"Kernel security label: {active_label}")
        if code != 0 or PROFILE not in active_label or "(enforce)" not in active_label:
            raise RuntimeError("Could not confirm the profile is enforcing")

        probe = [
            "python", "-c",
            "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000', timeout=2).read().decode())",
        ]
        for _ in range(30):
            container.reload()
            if container.status != "running":
                raise RuntimeError(container.logs().decode())
            code, output = container.exec_run(probe)
            if code == 0:
                print(f"Flask response under the profile: {output.decode().strip()}")
                break
            time.sleep(0.5)
        else:
            raise RuntimeError("Flask did not respond under the AppArmor profile")
        print("AppArmor SDK verification passed.")
    finally:
        if container is not None:
            container.remove(force=True)
            print("SDK verification container removed.")
        client.close()


if __name__ == "__main__":
    main()
