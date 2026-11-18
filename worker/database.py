import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient


# Locate the backend .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / "backend" / ".env"

# Load environment variables
load_dotenv(ENV_PATH)

# MongoDB connection variable
MONGO_URI = os.getenv("MONGO_URI")


def connect_database():

    if not MONGO_URI:
        raise ValueError("MONGO_URI is missing from backend/.env")

    # Create MongoDB connection
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    client.admin.command("ping")

    # Select database from the MongoDB URI
    database = client.get_default_database()

    if database is None:
        client.close()
        raise ValueError("No database name found in MONGO_URI")

    # Select tasks collection
    tasks_collection = database["tasks"]

    print("MongoDB connected successfully")
    print(f"Database: {database.name}")
    print("Collection: tasks")

    return client, database, tasks_collection
