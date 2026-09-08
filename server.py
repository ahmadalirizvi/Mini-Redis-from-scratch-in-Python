from storage import KeyValueStore
from parser import handle_command
import socket
import threading

HOST = "127.0.0.1"
PORT = 6380

subscribers = {}          # channel -> list of conn objects
subscribers_lock = threading.Lock()

def handle_client(conn, addr, store, lock):
    print(f"Connected by {addr}")
    subscribed_channels = []

    with conn:
        while True:
            data = conn.recv(1024)

            if not data:
                print(f"Disconnected: {addr}")
                # Clean up subscriptions on disconnect
                with subscribers_lock:
                    for channel in subscribed_channels:
                        if conn in subscribers.get(channel, []):
                            subscribers[channel].remove(conn)
                break

            message = data.decode().strip()
            print(f"Received from {addr}:", message)
            parts = message.split()

            if parts and parts[0].upper() == "SUBSCRIBE" and len(parts) == 2:
                channel = parts[1]
                with subscribers_lock:
                    subscribers.setdefault(channel, []).append(conn)
                subscribed_channels.append(channel)
                conn.sendall(f"Subscribed to {channel}\n".encode())
                continue

            if parts and parts[0].upper() == "PUBLISH" and len(parts) >= 3:
                channel = parts[1]
                msg_text = " ".join(parts[2:])
                sent_count = 0

                with subscribers_lock:
                    for sub_conn in subscribers.get(channel, []):
                        try:
                            sub_conn.sendall(f"{msg_text}\n".encode())
                            sent_count += 1
                        except OSError:
                            pass  # subscriber's socket died; ignore for now

                conn.sendall(f"Published to {sent_count} subscribers\n".encode())
                continue

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