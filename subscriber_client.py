import socket

HOST = "127.0.0.1"
PORT = 6380

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
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