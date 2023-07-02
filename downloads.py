import requests
import os
from urllib.parse import urlparse

def download_if_not_exists(downloadUrl, downloadPath):

    print("Handling download for " + downloadUrl)
    # from download url get the filename
    parsed_url = urlparse(downloadUrl)
    path = parsed_url.path
    filename = os.path.basename(path)

    # exit if the filename exists in the download directory
    full_download_path = os.path.join(downloadPath, filename)
    if(os.path.exists(full_download_path)):
       print("File already downloaded to " + downloadPath)
       return full_download_path
    
    print("Downloading " + downloadUrl)
    # download the file to the download direcotory
    audiofile = requests.get(downloadUrl)
    with open(full_download_path, 'wb') as f:
        f.write(audiofile.content)

    print("Downloaded to " + downloadPath)
    return full_download_path

class DownloadFile:
    def __init__(self, podcast_name, episode_title, download_folder, url_to_download):
        self.podcast_name = podcast_name
        self.episode_title = episode_title
        self.download_folder = download_folder
        self.url = url_to_download

class DownloadQueue:
    def __init__(self):
        self.to_download = []
        self.downloaded = []
