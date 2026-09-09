from storage import KeyValueStore
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

QUEUE_KEY = "jobs"
POLL_INTERVAL = 1  # seconds between checks when queue is empty


def process_job(job: str) -> None:
    """Simulate processing a single job from the queue."""
    logger.info(f"Processing job: {job}")
    time.sleep(1)  # simulate work being done
    logger.info(f"Finished job: {job}")


def main() -> None:
    store = KeyValueStore()
    logger.info(f"Worker started, watching queue: {QUEUE_KEY}")

    while True:
        store.load()  #