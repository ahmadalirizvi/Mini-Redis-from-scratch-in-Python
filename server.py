from storage import KeyValueStore
from parser import handle_command
import socket
import threading

HOST = "127.0.0.1"
PORT = 6380

def handle_client(conn, addr, store, lock):
    print(f"Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)

            if not data:
                print(f"Disconnected: {addr}")
                break

            message = data.decode().strip()
            print(f"Received from {addr}:", message)

            with lock:
                response = handle_command(store, message)

            conn.sendall((str(response) + "\n").encode())

def main():
    store = KeyValueStore()
    lock = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Mini Redis server listening on {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_client, args=(conn, addr, store, lock), daemon=True
            )
            thread.start()

if __name__ == "__main__":
    main()