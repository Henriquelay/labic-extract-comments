import requests
from exportcomments import ExportComments
from exportcomments.exceptions import ExportCommentsException
import time, sys, os
import pkg_resources

KEY = os.environ['EXPORT_COMMENTS_KEY']

ex = ExportComments(KEY)


# TODO change to webhook instead of busywaiting
def wait_for_job_blocking(guid: str):
    """Waits for the job to be done"""

    def get_job_status(guid) -> bool:
        """Checks if job is done"""
        response = ex.exports.check(guid=guid)
        status = response.body["data"][0]["status"]
        return status

    while (status := get_job_status(guid)) != "done":
        # Retry every 20 secs
        print(f"Job status: {status}. Waiting 20sec...")
        time.sleep(20)


def download_response(guid: str, download_url: str):
    wait_for_job_blocking(guid)

    headers = {
        "Authorization": KEY,
        "Content-Type": "application/json",
        "User-Agent": "python-sdk-{}".format(
            pkg_resources.get_distribution("exportcomments").version
        ),
    }

    response = requests.get(
        "https://exportcomments.com" + download_url, headers=headers
    )

    if response.status_code == 200:
        with open("result.xlsx", "wb") as output:
            output.write(response.content)
        print(f"[SUCCESSFUL DOWNLOAD] File Downloaded: {download_url}")
    else:
        print(f"[FAILED TO DOWNLOAD] Status Code: {response.status_code}")


if __name__ == "__main__":

    download_url = sys.argv[1]

    print(f"Downloading {download_url}")
    try:
        response = ex.exports.create(
            url=download_url,
            replies="false",
            twitterType=None,
        )
    except ExportCommentsException as e:
        print(f"Exception caught: {e}")
        sys.exit()

    guid = response.body["data"]["guid"]
    download_url = response.body["data"]["downloadUrl"]
    print(f"GUID: {guid}")
    print(f"Download URL: {download_url}")
    download_response(guid, download_url)
