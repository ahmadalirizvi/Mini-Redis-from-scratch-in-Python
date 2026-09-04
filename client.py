import socket

HOST = "127.0.0.1"
PORT = 6380

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"SET name Ahmad\n")
        response = s.recv(1024)
        print("Server said:", response.decode())

if __name__ == "__main__":
    main()