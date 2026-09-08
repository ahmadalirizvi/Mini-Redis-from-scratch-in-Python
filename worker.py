# worker.py
from storage import KeyValueStore
import time

QUEUE_KEY = "jobs"
POLL_INTERVAL = 1  # seconds between checks when queue is empty

def process_job(job):
    print(f"Processing job: {job}")
    time.sleep(1)  # simulate work being done
    print(f"Finished job: {job}")

def main():
    store = KeyValueStore()
    print("Worker started, watching queue:", QUEUE_KEY)

    while True:
        store.load()          # <-- new line: re-read database.json before checking
        job = store.lpop(QUEUE_KEY)

        if job is None:
            time.sleep(POLL_INTERVAL)
            continue

        process_job(job)

if __name__ == "__main__":
    main()