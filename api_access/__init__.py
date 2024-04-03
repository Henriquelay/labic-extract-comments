import time
import os
import requests

from exportcomments import ExportComments
from exportcomments.exceptions import ExportCommentsException


KEY = os.environ["EXPORT_COMMENTS_KEY"]

HEADERS = {
    "Authorization": KEY,
    # "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
    # "User-Agent": "python-sdk-1.0.1",
}

BASE_URL = "https://exportcomments.com"
API_URL = f"{BASE_URL}/api/v2"

ex = ExportComments(KEY)


def get_job_status(guid) -> bool:
    """Checks if job is done"""
    response = ex.exports.check(guid=guid)
    status = response.body["data"][0]["status"]
    return status


def download_raw(raw_url: str):
    """Downloads the raw results as JSON from the given URL"""

    response = requests.get(f"{BASE_URL}{raw_url}", headers=HEADERS, timeout=60)

    if response.status_code == 200:
        # print(response.content)
        # print(f"[SUCCESSFUL DOWNLOAD] File Downloaded: {raw_url}")
        return response.json()
    else:
        raise ExportCommentsException(response)


# TODO change to webhook instead of busywaiting
def download_json_blocking(guid: str, raw_url: str):
    """Periodically check the job and download the file when ready"""
    while (status := get_job_status(guid)) != "done":
        print(f"Job {guid} status: {status}. Waiting 30sec...")
        time.sleep(30)
    download_raw(raw_url)


def start_job(post_url: str) -> tuple[str, str]:
    """Starts the job on the remote server and returns the guid and raw_url of the job"""

    response = requests.put(
        f"{API_URL}/export",
        headers=HEADERS,
        timeout=30,  # Should be plenty since the job is started and returned immediately
        params={
            "url": post_url,
            "replies": "true",
        },
    )

    if response.status_code == 201:
        print(response.content)
        print(f"[STARTED]: {post_url}")
    else:
        print(f"[FAILED]: {post_url}\n{response.text}")
        raise ExportCommentsException(response)
    response = response.json()

    print(f"{response}")

    guid = response["data"]["guid"]
    raw_url = response["data"]["rawUrl"]
    print(f"Started job {guid}")
    return guid, raw_url
