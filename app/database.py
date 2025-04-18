from pymongo import MongoClient
import time
from fastapi.logger import logger

# Database connection settings
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "socialmedia"
COLLECTION_NAME = "posts"

# Initialize MongoDB client
retry_count = 0
max_retries = 5

while retry_count < max_retries:
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        logger.info("Database connection successful")
        break
    except Exception as e:
        logger.error(f"Connecting to database failed: {e}")
        retry_count += 1
        if retry_count < max_retries:
            time.sleep(2)
        else:
            logger.error("Max retries reached. Exiting.") 