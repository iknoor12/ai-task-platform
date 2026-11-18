import time
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

from database import connect_database
from processor import process_task
from redis_queue import (
    connect_redis,
    read_new_messages,
    reclaim_pending_messages,
    acknowledge_message,
    close_redis,
)


def add_log(tasks_collection, task_id, message):
    """Add a log entry to the task."""
    timestamp = datetime.now(timezone.utc).isoformat()

    tasks_collection.update_one(
        {"_id": task_id},
        {"$push": {"logs": f"{timestamp} - {message}"}}
    )


def process_message(
    message_id,
    fields,
    tasks_collection,
    reclaimed=False
):
    """Process one task received from the Redis stream."""

    task_id = fields.get("taskId")

    # Validate the Redis message
    if not task_id:
        print("Invalid message: taskId is missing")
        acknowledge_message(message_id)
        return

    try:
        task_object_id = ObjectId(task_id)
    except InvalidId:
        print(f"Invalid task ID: {task_id}")
        acknowledge_message(message_id)
        return

    # Check whether the task exists
    task = tasks_collection.find_one({"_id": task_object_id})

    if task is None:
        print(f"Task not found: {task_id}")
        acknowledge_message(message_id)
        return

    # Do not process already completed tasks again
    if task["status"] in ["success", "failed"]:
        print(f"Task already completed: {task_id}")
        acknowledge_message(message_id)
        return

    # Claim the task by changing its status to running.
    # Reclaimed messages may belong to a worker that previously crashed.
    allowed_statuses = ["pending", "running"] if reclaimed else ["pending"]

    claimed_task = tasks_collection.find_one_and_update(
        {
            "_id": task_object_id,
            "status": {"$in": allowed_statuses}
        },
        {
            "$set": {"status": "running"},
            "$push": {"logs": "Task processing started"}
        },
        return_document=ReturnDocument.AFTER
    )

    if claimed_task is None:
        print(f"Task could not be claimed: {task_id}")
        return

    print(f"Processing task: {task_id}")

    # Run the requested text operation
    try:
        result = process_task(
            claimed_task["inputText"],
            claimed_task["operation"]
        )

    except Exception as error:
        # Save the processing failure before acknowledging the message
        try:
            tasks_collection.update_one(
                {"_id": task_object_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(error)
                    },
                    "$push": {
                        "logs": f"Task failed: {error}"
                    }
                }
            )

            print(f"Task failed: {task_id}")
            acknowledge_message(message_id)

        except Exception as db_error:
            print(f"Could not save task failure: {db_error}")

        return

    # Save successful result
    try:
        tasks_collection.update_one(
            {"_id": task_object_id},
            {
                "$set": {
                    "status": "success",
                    "result": str(result)
                },
                "$push": {
                    "logs": "Task completed successfully"
                },
                "$unset": {"error": ""}
            }
        )

        print(f"Task completed: {task_id}")
        print(f"Result: {result}")

        # Acknowledge only after MongoDB has saved the result
        acknowledge_message(message_id)

    except Exception as error:
        print(f"Could not save task result: {error}")
        # Leave the message unacknowledged for later recovery


def main():

    mongo_client = None

    try:
        # Connect to MongoDB
        mongo_client, database, tasks_collection = connect_database()

        # Connect to Redis and create consumer group
        connect_redis()

        print("\nPython worker started. Waiting for tasks...\n")

        while True:

            # First recover messages left pending by crashed workers
            try:
                pending_messages = reclaim_pending_messages(
                    min_idle_time=60000,
                    count=5
                )

                for message_id, fields in pending_messages:
                    print("Recovering pending task:", message_id)

                    process_message(
                        message_id,
                        fields,
                        tasks_collection,
                        reclaimed=True
                    )

            except Exception as error:
                print("Pending-message recovery error:", error)

            # Read new messages
            try:
                messages = read_new_messages(count=5, block=5000)

                for stream_name, stream_messages in messages:
                    for message_id, fields in stream_messages:

                        process_message(
                            message_id,
                            fields,
                            tasks_collection
                        )

            except Exception as error:
                print("Redis message reading error:", error)
                time.sleep(3)

    except KeyboardInterrupt:
        print("\nWorker stopped by user.")

    except Exception as error:
        print("Worker startup error:", error)

    finally:
        close_redis()

        if mongo_client:
            mongo_client.close()

        print("Worker connections closed.")


if __name__ == "__main__":
    main()
