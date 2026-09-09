"""Simple test client for Mini Redis — sends a list of commands and prints responses."""

import socket
import time
from config import HOST, PORT, AUTH_PASSWORD


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        commands = [
            f"AUTH {AUTH_PASSWORD}",
            "SET name Ahmad",
            "GET name",
        ]

        for cmd in commands:
            s.sendall((cmd + "\n").encode())
            response = s.recv(1024)
            print(f"> {cmd}")
            print("Server said:", response.decode())
            time.sleep(0.1)  # small pause; bump to 2 for manual concurrency testing


if __name__ == "__main__":
    main()