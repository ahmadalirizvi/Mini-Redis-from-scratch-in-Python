import socket
import time         

HOST = "127.0.0.1"
PORT = 6380

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # commands = [
        #     "RPUSH jobs send_email",
        #     "RPUSH jobs resize_image",
        #     "RPUSH jobs generate_report",
        # ]
        commands = [
            "PUBLISH notifications New message from Ahmad",
        ]

        for cmd in commands:
            s.sendall((cmd + "\n").encode())
            response = s.recv(1024)
            print(f"> {cmd}")
            print("Server said:", response.decode())
            time.sleep(2)

if __name__ == "__main__":
    main()