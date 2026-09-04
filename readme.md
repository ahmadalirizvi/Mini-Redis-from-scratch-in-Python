# Project In Progress
# Mini Redis From Scratch in Python

A learning focused Redis like in memory key value store being built from scratch in Python.
The goal of this project is to understand how systems like Redis work internally by implementing their core concepts step by step without using the Redis server or the `redis` Python package.

## Project Goals

This project aims to explore and implement:

* In memory key value storage
* Command parsing
* Key expiration and TTL
* Data persistence
* TCP networking
* Multiple client connections
* Redis like data structures
* Rate limiting
* Background job queues
* Pub/Sub
* Authentication
* Performance optimization
* Automated testing

The project is being developed phase by phase, with each phase introducing a new backend or systems concept.

## Architecture

The project starts as a simple Python class using a dictionary and gradually evolves into a networked Redis like server.

### Initial Architecture

```text
┌──────────────────────┐
│     Python Program   │
│                      │
│    KeyValueStore     │
│          │           │
│          ▼           │
│      Python dict     │
└──────────────────────┘
```

### Final Target Architecture

```text
                    ┌─────────────────┐
                    │     Client      │
                    └────────┬────────┘
                             │
                             │ TCP
                             ▼
                    ┌─────────────────┐
                    │  Mini Redis     │
                    │     Server      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Command Parser  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌───────────┐   ┌──────────┐
        │  String  │   │   Lists   │   │  Sets    │
        └──────────┘   └───────────┘   └──────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │   Data Store    │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │ Persistence  │      │    Expiry    │
          └──────────────┘      └──────────────┘
```

## Tech Stack

* Python 3
* Python Standard Library
* TCP Sockets
* JSON
* File I/O
* Threading and concurrency
* Unit testing

No external Redis server is required for the core project.

## Project Structure

The project structure will evolve as new features are added.

```text
mini-redis/
│
├── main.py
├── client.py
├── storage.py
├── parser.py
├── persistence.py
├── config.py
│
├── tests/
│   ├── test_storage.py
│   ├── test_expiry.py
│   ├── test_commands.py
│   └── test_server.py
│
├── data/
│   └── database.json
│
├── README.md
├── requirements.txt
└── .gitignore
```

During the early phases, the project may contain only:

```text
mini-redis/
│
├── main.py
├── README.md
└── .venv/
```

The codebase will become more modular as the project grows.

# Development Roadmap

## Phase 1: Basic Key Value Store

### Objective

Build the basic storage engine using a Python dictionary.

The first version supports:

```text
SET
GET
DELETE
EXISTS
```

### Example

```text
> SET name Ahmad
OK

> GET name
Ahmad

> EXISTS name
True

> DELETE name
OK

> GET name
(nil)
```

### Concepts

* Python dictionaries
* Classes
* Methods
* Key value storage
* CRUD operations
* Basic data management

### Status

**In Progress**

---

## Phase 2: TTL and Key Expiration

### Objective

Add the ability to automatically expire keys after a specified amount of time.

Example:

```text
SET session abc123 EX 60
```

The key should expire after 60 seconds.

```text
> GET session
abc123
```

After expiration:

```text
> GET session
(nil)
```

### TTL Command

Add support for:

```text
TTL session
```

Example:

```text
> SET session abc123 EX 60
OK

> TTL session
57
```

### TTL Return Values

```text
-1    Key exists but has no expiration
-2    Key does not exist or has expired
```

### Concepts

* `time.time()`
* Timestamps
* TTL
* Expiration
* Lazy expiration
* Temporary data
* Cache behavior

### Status

**In Progress**

---

## Phase 3: Persistence

### Objective

Make stored data survive application restarts.

Currently:

```text
Start server
    ↓
Store data
    ↓
Stop server
    ↓
Data disappears
```

Target:

```text
Start server
    ↓
Store data
    ↓
Save data
    ↓
Stop server
    ↓
Start server
    ↓
Load data
```

Example:

```text
> SET name Ahmad
OK
```

After restarting:

```text
> GET name
Ahmad
```

### Initial Approach

The first implementation will use JSON for learning purposes.

### Concepts

* File I/O
* Serialization
* Deserialization
* Persistence
* Data recovery
* Memory vs disk storage

### Status

**Planned**

---

## Phase 4: TCP Networking

### Objective

Turn the Mini Redis application into an actual server that clients can connect to.

Target architecture:

```text
Client
   │
   │ TCP
   ▼
Mini Redis Server
   │
   ▼
KeyValueStore
```

### Example

Start the server:

```bash
python main.py
```

Start the client:

```bash
python client.py
```

Then:

```text
> SET name Ahmad
OK

> GET name
Ahmad
```

### Concepts

* TCP
* Sockets
* Ports
* Client server architecture
* Network communication
* Request and response systems

### Status

**Planned**

---

## Phase 5: Command Parser

### Objective

Build a proper command parser.

Instead of directly calling Python methods:

```python
store.set("name", "Ahmad")
```

the client will send:

```text
SET name Ahmad
```

The parser converts the command into a structured operation.

```text
SET name Ahmad
       │
       ▼
┌─────────────┐
│   Parser    │
└──────┬──────┘
       │
       ▼
Command = SET
Key     = name
Value   = Ahmad
```

### Concepts

* String parsing
* Tokenization
* Validation
* Error handling
* Command protocols

### Status

**Planned**

---

## Phase 6: Multiple Clients and Concurrency

### Objective

Allow multiple clients to connect to the server simultaneously.

```text
Client 1 ──┐
Client 2 ──┤
Client 3 ──┼──> Mini Redis Server
Client 4 ──┤
Client 5 ──┘
```

### Concepts

* Concurrency
* Threads
* Shared state
* Race conditions
* Locks
* Thread safety

### Status

**Planned**

---

## Phase 7: Redis Like Data Structures

### Objective

Support multiple data structures instead of only simple key value pairs.

### Strings

```text
SET name Ahmad
GET name
```

### Lists

```text
LPUSH users Ahmad
LPUSH users Ali
```

### Sets

```text
SADD skills Python
SADD skills Redis
```

### Hashes

```text
HSET user:1 name Ahmad
HSET user:1 age 21
```

### Sorted Sets

```text
ZADD leaderboard 100 Ahmad
ZADD leaderboard 200 Ali
```

### Concepts

* Lists
* Sets
* Hash maps
* Sorting
* Data modeling
* Algorithmic thinking

### Status

**Planned**

---

## Phase 8: Rate Limiting

### Objective

Implement a rate limiter using the Mini Redis storage engine.

Example:

```text
Maximum: 100 requests per minute
```

Conceptually:

```text
user:123:requests → 57
```

Request flow:

```text
Request
   ↓
Check counter
   ↓
Under limit?
   │
   ├── Yes → Allow
   │
   └── No  → Reject
```

### Concepts

* Counters
* TTL
* Rate limiting
* API protection
* Atomic operations

### Status

**Planned**

---

## Phase 9: Background Job Queue

### Objective

Implement a basic job queue.

```text
Web Application
      │
      ▼
   Job Queue
      │
      ▼
    Worker
      │
      ▼
 Process Job
```

Possible jobs:

```text
send_email
resize_image
process_video
generate_report
```

### Concepts

* Queues
* Workers
* Background processing
* Producer consumer architecture
* Task processing

### Status

**Planned**

---

## Phase 10: Pub/Sub

### Objective

Implement a basic Publish and Subscribe system.

```text
Publisher
    │
    ▼
 Redis Channel
    │
 ┌──┴──────────┐
 ▼             ▼
Subscriber 1  Subscriber 2
```

Example:

```text
SUBSCRIBE notifications
```

Another client:

```text
PUBLISH notifications "New message"
```

Subscribers receive:

```text
New message
```

### Concepts

* Pub/Sub
* Messaging
* Event driven architecture
* Real time communication

### Status

**Planned**

---

## Phase 11: Authentication

### Objective

Add basic authentication to the server.

Example:

```text
AUTH mypassword
```

Only authenticated clients will be able to execute protected commands.

### Concepts

* Authentication
* Authorization
* Connection state
* Security fundamentals

> This implementation is for educational purposes and should not be considered production grade security.

### Status

**Planned**

---

## Phase 12: Performance and Optimization

### Objective

Measure the performance of the Mini Redis server and identify bottlenecks.

Tests will measure:

* SET operations
* GET operations
* DELETE operations
* TTL operations
* Concurrent clients
* Memory usage
* CPU usage
* Latency
* Throughput

Example benchmark:

```text
Operations: 100,000
GET requests: 100,000
Average latency: XX ms
Requests per second: XXXX
```

### Concepts

* Benchmarking
* Profiling
* Optimization
* Latency
* Throughput
* Performance engineering

### Status

**Planned**

---

## Phase 13: Automated Testing

### Objective

Create automated tests for every major component.

Example:

```text
tests/
├── test_storage.py
├── test_expiry.py
├── test_commands.py
├── test_persistence.py
└── test_server.py
```

Test cases will include:

```text
SET stores a value
GET returns a value
GET handles missing keys
DELETE removes a key
EXISTS checks a key
TTL expires a key
Persistence restores data
Multiple clients work correctly
Invalid commands are handled correctly
```

### Status

**Planned**

---

## Phase 14: Documentation and Code Quality

### Objective

Improve the project structure and make the code easier to understand and maintain.

Tasks:

* Add type hints
* Add docstrings
* Improve error handling
* Add logging
* Add configuration
* Improve project structure
* Add documentation
* Add examples
* Add benchmarks
* Refactor duplicated code
* Improve test coverage

### Status

**Planned**

# Current Progress

| Phase | Feature               | Status      |
| ----- | --------------------- | ----------- |
| 1     | Basic Key Value Store | Completed   |
| 2     | TTL and Expiration    | In Progress |
| 3     | Persistence           | Planned     |
| 4     | TCP Networking        | Planned     |
| 5     | Command Parser        | Planned     |
| 6     | Multiple Clients      | Planned     |
| 7     | Data Structures       | Planned     |
| 8     | Rate Limiting         | Planned     |
| 9     | Job Queue             | Planned     |
| 10    | Pub/Sub               | Planned     |
| 11    | Authentication        | Planned     |
| 12    | Performance           | Planned     |
| 13    | Automated Testing     | Planned     |
| 14    | Documentation         | Planned     |

# Installation

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd mini-redis
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

## 3. Activate the virtual environment

### macOS and Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## 4. Run the project

During the early phases:

```bash
python main.py
```

# Example Commands

The final Mini Redis interface is planned to support commands such as:

```text
SET key value
GET key
DELETE key
EXISTS key
TTL key

SET key value EX 60

LPUSH list value
SADD set value

HSET hash field value

PUBLISH channel message
SUBSCRIBE channel
```

More commands will be added as development continues.

# Learning Objectives

This project is being built to understand:

* How key value stores work
* How caching works
* How TTL and expiration work
* How persistence works
* How TCP servers work
* How clients communicate with servers
* How concurrency works
* How queues work
* How Pub/Sub works
* How rate limiting works
* How different data structures affect performance
* How memory and disk storage differ
* How backend systems can be benchmarked
* How scalable services are designed

# Why Build Redis From Scratch?

Using Redis is simple:

```python
import redis

client = redis.Redis()

client.set("name", "Ahmad")
print(client.get("name"))
```

However, using Redis does not necessarily explain how Redis works internally.

Building a simplified version from scratch makes it possible to explore:

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

The purpose of this project is not to replace Redis.

The purpose is to understand the concepts and engineering decisions behind systems like Redis.

# Development Philosophy

The project follows an incremental learning approach.

Instead of implementing everything at once:

```text
❌ Build everything at once
```

the project follows:

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

Each phase builds upon the previous phase.

# Disclaimer

This is an educational implementation inspired by the concepts found in Redis.

It is not intended to be a production replacement for Redis.

The project prioritizes:

1. Understanding
2. Simplicity
3. Experimentation
4. Clean implementation
5. Gradual complexity

# Author

**Ahmad Ali**
Built from scratch in Python as a learning project.

# Roadmap

```text
[✓] Phase 1  Basic Key Value Store
[ ] Phase 2  TTL and Expiration
[ ] Phase 3  Persistence
[ ] Phase 4  TCP Networking
[ ] Phase 5  Command Parser
[ ] Phase 6  Multiple Clients
[ ] Phase 7  Data Structures
[ ] Phase 8  Rate Limiting
[ ] Phase 9  Job Queue
[ ] Phase 10 Pub/Sub
[ ] Phase 11 Authentication
[ ] Phase 12 Performance
[ ] Phase 13 Automated Testing
[ ] Phase 14 Documentation
```

> Building a Redis like database from scratch in Python to understand how it works under the hood.
