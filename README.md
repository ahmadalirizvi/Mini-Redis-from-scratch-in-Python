# Mini Redis From Scratch in Python

A learning-focused implementation of a Redis-like in-memory key-value store built from scratch in Python.

The goal of this project was to understand how systems like Redis work internally by implementing their core concepts step by step, without using the Redis server or the `redis` Python package.

**Status: All 14 phases completed.** From a plain Python dictionary to a threaded, persistent, authenticated, Pub/Sub-capable key-value server with multiple data structures, rate limiting, a background job queue, and an automated test suite.

## Project Goals

This project explores and implements:

* In-memory key-value storage
* Command parsing
* Key expiration and TTL
* Data persistence
* TCP networking
* Multiple client connections
* Redis-like data structures
* Rate limiting
* Background job queues
* Pub/Sub
* Authentication
* Performance optimization
* Automated testing

The project was developed phase by phase, with each phase introducing a new backend or systems concept.

## Architecture

The project started as a simple Python class using a dictionary and evolved into a networked, multi-client, persistent Redis-like server.

### Initial Architecture

```text
┌──────────────────────┐
│     Python Program    │
│                       │
│    KeyValueStore      │
│          │            │
│          ▼            │
│      Python dict      │
└──────────────────────┘
```

### Final Architecture

```text
                    ┌─────────────────┐
                    │     Client       │
                    └────────┬────────┘
                             │
                             │ TCP
                             ▼
                    ┌─────────────────┐
                    │  Mini Redis      │
                    │     Server       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Command Parser   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌───────────┐   ┌──────────┐
        │  String   │   │   Lists   │   │  Sets     │
        └──────────┘   └───────────┘   └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │   Data Store     │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │ Persistence   │      │    Expiry     │
          └──────────────┘      └──────────────┘
```

## Tech Stack

* Python 3
* Python Standard Library
* TCP Sockets
* JSON
* File I/O
* Threading and concurrency
* `logging` module
* Unit testing with `pytest`

No external Redis server or `redis` package is used anywhere in this project.

## Project Structure

```text
mini-redis/
│
├── server.py              # TCP server, connection handling, threading, auth, Pub/Sub
├── client.py               # Example client sending a batch of commands
├── subscriber_client.py    # Listen-only client for Pub/Sub testing
├── worker.py                # Background worker that drains the job queue
├── storage.py               # KeyValueStore — the core storage engine
├── parser.py                 # Translates raw text commands into store calls
├── config.py                  # HOST, PORT, AUTH_PASSWORD, DB path, save interval
├── benchmark.py                # Throughput/latency benchmark script
│
├── tests/
│   ├── __init__.py
│   ├── test_storage.py         # SET/GET/DELETE/EXISTS
│   ├── test_expiry.py           # TTL and expiration behavior
│   ├── test_persistence.py       # save/load roundtrip, corrupt/missing file handling
│   └── test_commands.py           # Parser-level command handling
│
├── data/
│   └── database.json               # Persisted store (JSON, git-ignored)
│
├── README.md
├── .gitignore
└── requirements.txt
```

# Development Roadmap

| Phase | Feature                | Status    |
| ----- | ----------------------- | --------- |
| 1     | Basic Key-Value Store    | Completed |
| 2     | TTL and Expiration        | Completed |
| 3     | Persistence                | Completed |
| 4     | TCP Networking               | Completed |
| 5     | Command Parser                 | Completed |
| 6     | Multiple Clients                 | Completed |
| 7     | Data Structures                    | Completed |
| 8     | Rate Limiting                        | Completed |
| 9     | Job Queue                              | Completed |
| 10    | Pub/Sub                                  | Completed |
| 11    | Authentication                             | Completed |
| 12    | Performance                                  | Completed |
| 13    | Automated Testing                              | Completed |
| 14    | Documentation                                    | Completed |

```text
[✓] Phase 1  Basic Key Value Store
[✓] Phase 2  TTL and Expiration
[✓] Phase 3  Persistence
[✓] Phase 4  TCP Networking
[✓] Phase 5  Command Parser
[✓] Phase 6  Multiple Clients
[✓] Phase 7  Data Structures
[✓] Phase 8  Rate Limiting
[✓] Phase 9  Job Queue
[✓] Phase 10 Pub/Sub
[✓] Phase 11 Authentication
[✓] Phase 12 Performance
[✓] Phase 13 Automated Testing
[✓] Phase 14 Documentation
```

---

## Phase Summaries

### Phase 1 — Basic Key Value Store
A `KeyValueStore` class backed by a Python `dict`, supporting `SET`, `GET`, `DELETE`, and `EXISTS`.

### Phase 2 — TTL and Key Expiration
Keys can be set with an expiration (`SET key value EX seconds`). Expiration is lazy — checked and cleaned up whenever a key is accessed via `GET`, `TTL`, or `EXISTS`, not by a background sweep. `TTL` returns `-1` for a key with no expiry and `-2` for a missing or expired key.

### Phase 3 — Persistence
Data is saved to `data/database.json` and reloaded on startup, so the store survives restarts. `load()` gracefully handles a missing, empty, or corrupt file by starting fresh instead of crashing.

### Phase 4 — TCP Networking
`server.py` and `client.py` communicate over a raw TCP socket, replacing direct in-process method calls with real request/response messages.

### Phase 5 — Command Parser
`parser.py` turns raw text like `SET name Ahmad` into real calls against `KeyValueStore`, with argument validation and clear `ERR` messages for malformed commands.

### Phase 6 — Multiple Clients and Concurrency
The server spawns a thread per connection so multiple clients can be served at once. A `threading.Lock` protects all access to the shared `KeyValueStore`, preventing race conditions and corrupted saves when multiple clients write concurrently.

### Phase 7 — Redis-Like Data Structures
Beyond strings, the store supports:
* **Lists** — `LPUSH`, `RPUSH`, `LRANGE`, `LPOP`, `LLEN`
* **Sets** — `SADD`, `SMEMBERS`, `SREM` (Python `set` internally; serialized as a tagged list for JSON, since JSON has no native set type)
* **Hashes** — `HSET`, `HGET`, `HGETALL`
* **Sorted Sets** — `ZADD`, `ZRANGE`, `ZSCORE` (member → score, sorted at read time)

### Phase 8 — Rate Limiting
A fixed-window rate limiter (`RATE_LIMIT key max_requests window_seconds`) built entirely on the store's own counter and TTL mechanics — no separate system required.

### Phase 9 — Background Job Queue
`RPUSH` (tail-insert) combined with the existing `LPOP` (head-remove) gives FIFO queue semantics. `worker.py` runs as a separate process, polling the queue and reloading the store from disk each cycle to see jobs added by other processes.

### Phase 10 — Pub/Sub
Clients can `SUBSCRIBE` to a channel and receive messages pushed in real time when another client `PUBLISH`es to it — no polling. This is the first phase where the server actively pushes data to a client rather than only responding to requests.

### Phase 11 — Authentication
Clients must send `AUTH <password>` before any other command is accepted. Auth state is tracked per-connection. The password lives in `config.py` — hardcoded for learning purposes; **not production-grade security**.

### Phase 12 — Performance and Optimization
**Finding:** early benchmarks showed `SET`/`DELETE` throughput at roughly **600 ops/sec**, dramatically lower than `GET`'s ~15,000–19,000 ops/sec, despite `GET` doing no disk I/O at all. The cause: `save()` rewrote the *entire* `database.json` file on every single mutation — an O(n) cost per write that scales with total dataset size.

**Fix:** replaced save-on-every-write with a dirty-flag + periodic flush pattern — mutating methods set `self._dirty = True`, and a background thread flushes to disk once per second (plus once more on clean shutdown).

**Result:**

| Operation | Before      | After         |
| --------- | ----------- | -------------- |
| SET       | ~600 ops/s  | ~9,800 ops/s   |
| DELETE    | ~630 ops/s  | ~7,850 ops/s   |
| GET       | ~15–19k ops/s | ~14k ops/s (unchanged, as expected) |

**Trade-off:** writes are no longer durable immediately — up to one second of recent writes could be lost in a crash. This mirrors real tunable durability knobs in production databases (Redis's `save` intervals, PostgreSQL's `synchronous_commit`): faster writes in exchange for a small durability window.

### Phase 13 — Automated Testing
A `pytest` suite (17 tests) covering storage basics, TTL/expiration, persistence (including corrupt/missing file handling), and parser-level command handling. All tests use the `tmp_path` fixture so no test data is ever written to the real project directory.

### Phase 14 — Documentation and Code Quality
Type hints and docstrings added across `storage.py` and `parser.py`. `print()` replaced with the `logging` module (timestamped, leveled output) in `server.py` and `worker.py`. Configuration consolidated into `config.py` instead of being duplicated across files. Repeated argument-validation logic in `parser.py` extracted into a `require_args()` helper.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ahmadalirizvi/Mini-Redis-from-scratch-in-Python
cd mini-redis
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

Currently only `pytest` is required, for the test suite — the server itself uses only the standard library.

## Quick Start

Start the server:

```bash
python server.py
```

In a separate terminal, connect with the client (or write your own using raw sockets). All commands after `AUTH` require authentication first — the password is set in `config.py`.

```text
> AUTH changeme123
OK

# Strings
> SET name Ahmad
OK
> GET name
Ahmad
> SET session abc123 EX 60
OK
> TTL session
57
> DELETE name
OK

# Lists
> RPUSH jobs send_email
OK
> RPUSH jobs resize_image
OK
> LRANGE jobs
send_email resize_image
> LPOP jobs
send_email
> LLEN jobs
1

# Sets
> SADD skills Python
OK
> SADD skills Redis
OK
> SMEMBERS skills
Python Redis
> SREM skills Redis
OK

# Hashes
> HSET user:1 name Ahmad
OK
> HSET user:1 age 21
OK
> HGET user:1 name
Ahmad
> HGETALL user:1
name Ahmad age 21

# Sorted Sets
> ZADD leaderboard 100 Ahmad
OK
> ZADD leaderboard 250 Ali
OK
> ZRANGE leaderboard
Ahmad Ali
> ZSCORE leaderboard Ali
250.0

# Rate Limiting
> RATE_LIMIT user:123 3 10
ALLOWED
> RATE_LIMIT user:123 3 10
ALLOWED
> RATE_LIMIT user:123 3 10
ALLOWED
> RATE_LIMIT user:123 3 10
REJECTED
```

### Pub/Sub

Run `subscriber_client.py` in one terminal:

```bash
python subscriber_client.py
```

Then, from another terminal, publish to the same channel:

```text
> PUBLISH notifications New message from Ahmad
Published to 1 subscribers
```

The subscriber terminal will immediately print the message — no polling.

### Background Job Queue

Run `worker.py` alongside the server:

```bash
python worker.py
```

Anything pushed to the `jobs` list via `RPUSH` will be picked up and processed automatically:

```text
> RPUSH jobs send_email
OK
> RPUSH jobs resize_image
OK
```

### Running Tests

```bash
pytest -v
```

### Running the Benchmark

```bash
python benchmark.py
```

## Full Command Reference

```text
AUTH password

SET key value
SET key value EX seconds
GET key
DELETE key
EXISTS key
TTL key
INCR key

LPUSH key value
RPUSH key value
LRANGE key
LPOP key
LLEN key

SADD key value
SMEMBERS key
SREM key value

HSET key field value
HGET key field
HGETALL key

ZADD key score member
ZRANGE key
ZSCORE key member

RATE_LIMIT key max_requests window_seconds

SUBSCRIBE channel
PUBLISH channel message
```

## Learning Objectives

This project was built to understand:

* How key-value stores work
* How caching works
* How TTL and expiration work
* How persistence works, and the trade-offs in *when* to persist
* How TCP servers work
* How clients communicate with servers
* How concurrency and thread safety work
* How queues and producer/consumer systems work
* How Pub/Sub and real-time push differ from request/response
* How rate limiting works
* How different data structures affect what a store can do
* How memory and disk storage differ
* How backend systems are benchmarked and optimized
* How to structure a codebase, document it, and test it as it grows

## Why Build Redis From Scratch?

Using Redis is simple:

```python
import redis

client = redis.Redis()
client.set("name", "Ahmad")
print(client.get("name"))
```

But using Redis doesn't explain how Redis works internally. Building a simplified version from scratch makes it possible to actually hit — and solve — the real problems Redis solves:

```text
Storage
   ↓
Expiration
   ↓
Persistence
   ↓
Networking
   ↓
Concurrency
   ↓
Data Structures
   ↓
Messaging
   ↓
Performance
```

The purpose was never to replace Redis — it's to understand the engineering decisions behind systems like it, by making (and fixing) the same kinds of mistakes a real implementation has to deal with.

## Development Philosophy

The project followed an incremental, phase-by-phase approach:

```text
Phase
  ↓
Understand
  ↓
Implement
  ↓
Test
  ↓
Improve
  ↓
Next Phase
```

Several real bugs surfaced and were fixed along the way — missing `save()` calls after mutations, import-time side effects in `storage.py`, a file path resolving relative to the wrong working directory, and a stale server process quietly holding a port after a crash. Each one became a small lesson in its own right, which is arguably the actual point of building something like this from scratch rather than just reading about how Redis works.

## Disclaimer

This is an educational implementation inspired by the concepts found in Redis. It is **not** intended to be a production replacement for Redis, and the authentication system in particular (Phase 11) is for learning purposes only — not production-grade security.

The project prioritizes:

1. Understanding
2. Simplicity
3. Experimentation
4. Clean implementation
5. Gradual complexity

## License

This project is intended for educational purposes.

```text
MIT License
```

## Author

**Ahmad Ali**

Built from scratch in Python as a learning project — from a plain dictionary to a threaded, persistent, authenticated, Pub/Sub-capable key-value server with multiple data structures, rate limiting, a background job queue, and an automated test suite.
