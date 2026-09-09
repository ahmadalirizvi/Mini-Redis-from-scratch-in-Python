"""Benchmark script for Mini Redis — measures SET/GET/DELETE throughput and latency."""

import socket
import time
from config import HOST, PORT, AUTH_PASSWORD

NUM_OPERATIONS = 2000


def send_command(sock: socket.socket, command: str) -> bytes:
    sock.sendall((command + "\n").encode())
    return sock.recv(1024)


def benchmark_set(sock: socket.socket) -> float:
    start = time.time()
    for i in range(NUM_OPERATIONS):
        send_command(sock, f"SET key{i} value{i}")
    return time.time() - start


def benchmark_get(sock: socket.socket) -> float:
    start = time.time()
    for i in range(NUM_OPERATIONS):
        send_command(sock, f"GET key{i}")
    return time.time() - start


def benchmark_delete(sock: socket.socket) -> float:
    start = time.time()
    for i in range(NUM_OPERATIONS):
        send_command(sock, f"DELETE key{i}")
    return time.time() - start


def report(name: str, elapsed: float, count: int) -> None:
    avg_latency_ms = (elapsed / count) * 1000
    ops_per_sec = count / elapsed
    print(f"{name}:")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Avg latency: {avg_latency_ms:.3f} ms")
    print(f"  Throughput: {ops_per_sec:.1f} ops/sec")
    print()


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        send_command(sock, f"AUTH {AUTH_PASSWORD}")

        report("SET", benchmark_set(sock), NUM_OPERATIONS)
        report("GET", benchmark_get(sock), NUM_OPERATIONS)
        report("DELETE", benchmark_delete(sock), NUM_OPERATIONS)


if __name__ == "__main__":
    main()