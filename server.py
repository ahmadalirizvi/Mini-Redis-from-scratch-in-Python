from storage import KeyValueStore
import socket

HOST = "127.0.0.1"
PORT = 6380

def main():
    store = KeyValueStore()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Mini Redis server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                while True:
                    data = conn.recv(1024)

                    if not data:
                        # Client closed the connection
                        print(f"Disconnected: {addr}")
                        break

                    message = data.decode().strip()
                    print("Received:", message)

                    conn.sendall(b"OK\n")

if __name__ == "__main__":
    main()