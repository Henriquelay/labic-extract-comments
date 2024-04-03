# pylint: disable=redefined-outer-name

import sys
import os
from multiprocessing import Pool

from exportcomments.exceptions import ExportCommentsException
from pymongo import MongoClient

import api_access

MONGO_URI = os.environ["MONGO_URI"]

mongodb = MongoClient(MONGO_URI)
db = mongodb.export_comments


def store_on_database(guid: str, raw_url: str):
    """Stores the downloaded file on the database"""
    collection = db.tiktok
    # TODO
    collection.insert_one({"guid": guid, "raw_url": raw_url})    


if __name__ == "__main__":
    urls = sys.argv[1:]

    # Spawns a executor process pool with `j` workers, where `j` is the available parallelism (usually CPU cores)
    with Pool() as pool:
        # Only 5 in progress tasks are allowed, exceeding are queued up to 5.
        # Throttled to 5 requests per second. 
        running_jobs = 0
        for post_url in urls:
            if running_jobs >= 5:
                print("Waiting for a job to finish...")
                pool.join()
                running_jobs -= 1

            try:
                guid, raw_url = api_access.start_job(post_url)
            except ExportCommentsException as e:
                print(f"Error: {e}")
                continue
            running_jobs += 1
            
            # Assign a worker to periodically check the job status and download the file when ready
            pool.apply_async(api_access.download_json_blocking, args=(guid, raw_url))
        # Wait for all jobs on pool to end
        pool.close()
