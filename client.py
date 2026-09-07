import socket
import time         

HOST = "127.0.0.1"
PORT = 6380

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        commands = [
            "SET name Ahmad",
            "GET name",
            "SET session fresh EX 30",
            "TTL session",
            "GET session",
            "EXISTS session",
            "DELETE name",
            "GET name",
        ]

        for cmd in commands:
            s.sendall((cmd + "\n").encode())
            response = s.recv(1024)
            print(f"> {cmd}")
            print("Server said:", response.decode())
            time.sleep(2)

if __name__ == "__main__":
    main()