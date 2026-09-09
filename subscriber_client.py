"""Listen-only client for Mini Redis Pub/Sub — subscribes and prints incoming messages."""

import socket
from config import HOST, PORT, AUTH_PASSWORD


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        s.sendall(f"AUTH {AUTH_PASSWORD}\n".encode())
        print(s.recv(1024).decode().strip())

        s.sendall(b"SUBSCRIBE notifications\n")
        print(s.recv(1024).decode().strip())

        print("Listening for messages...")
        while True:
            data = s.recv(1024)
            if not data:
                break
            print("Received:", data.decode().strip())


if __name__ == "__main__":
    main()