import os
import socket
import uuid
from pathlib import Path

import redis
from dotenv import load_dotenv


# Load backend environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / "backend" / ".env")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

STREAM_NAME = "task_stream"
GROUP_NAME = "task_workers"

# Unique name for every worker instance
CONSUMER_NAME = f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"

# Connect to Redis
redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def connect_redis():
    """Test Redis connection and create consumer group."""

    redis_client.ping()
    print("Redis connected successfully")

    try:
        redis_client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True
        )
        print(f"Consumer group created: {GROUP_NAME}")

    except redis.exceptions.ResponseError as error:
        if "BUSYGROUP" in str(error):
            print(f"Consumer group already exists: {GROUP_NAME}")
        else:
            raise


def read_new_messages(count=5, block=5000):
    """Read new messages from Redis."""

    messages = redis_client.xreadgroup(
        groupname=GROUP_NAME,
        consumername=CONSUMER_NAME,
        streams={STREAM_NAME: ">"},
        count=count,
        block=block
    )

    return messages


def reclaim_pending_messages(min_idle_time=60000, count=5):
    """Recover messages abandoned by other workers."""

    result = redis_client.xautoclaim(
        STREAM_NAME,
        GROUP_NAME,
        CONSUMER_NAME,
        min_idle_time,
        "0-0",
        count=count
    )

    return result[1]


def acknowledge_message(message_id):
    """Acknowledge a processed Redis message."""

    return redis_client.xack(
        STREAM_NAME,
        GROUP_NAME,
        message_id
    )


def close_redis():
    redis_client.close()
