import docker

IMAGE = "flask-apparmor:lab05"
PROFILE = "my-apparmor-profile"


def main():
    client = docker.from_env()
    container = None
    try:
        container = client.containers.run(
            IMAGE, security_opt=[f"apparmor={PROFILE}"], detach=True
        )
        container.reload()
        if container.attrs["AppArmorProfile"] != PROFILE:
            raise RuntimeError("The expected profile was not applied")

        code, output = container.exec_run(
            ["python", "-c", "from pathlib import Path; print(Path('/proc/self/attr/current').read_text())"]
        )
        active_label = output.decode().strip()
        print(f"Kernel security label: {active_label}")
        if code != 0 or PROFILE not in active_label or "(enforce)" not in active_label:
            raise RuntimeError("Could not confirm the profile is enforcing")

        # Python is outside /usr/bin, so this tests the file-read rule directly.
        code, output = container.exec_run(
            ["python", "-c", "open('/etc/passwd').read(); print('Read succeeded')"]
        )
        print(f"Read /etc/passwd: exit code {code}")
        print(output.decode().strip())
        if code == 0 or "PermissionError" not in output.decode():
            raise RuntimeError("Expected an AppArmor file-read permission denial")

        # runc applies a profile on the initial exec. Test a later exec from
        # Python while it is already confined, matching an application's action.
        bash_probe = (
            "import subprocess; from pathlib import Path; "
            "print('Launcher label:', Path('/proc/self/attr/current').read_text().strip(), flush=True); "
            "subprocess.run(['/bin/bash', '-c', 'echo bash-executed'], check=True)"
        )
        code, output = container.exec_run(["python", "-c", bash_probe])
        message = output.decode().strip()
        print(f"Launch /bin/bash from confined Python: exit code {code}")
        print(message)
        if code == 0 or "PermissionError" not in message or "/bin/bash" not in message:
            raise RuntimeError("Expected an AppArmor execution permission denial")

        print("Both restricted actions were denied as expected.")
    finally:
        if container is not None:
            container.remove(force=True)
            print("Restriction-test container removed.")
        client.close()


if __name__ == "__main__":
    main()
