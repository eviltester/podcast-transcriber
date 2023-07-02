# pyyaml just for printing for debugging convenience
import yaml
import os
from downloads import DownloadFile, DownloadQueue, download_if_not_exists
from transcriber import transcribe

#
# Main App code
#


'''
Todo List
TODO: download files into podcast specific named folders
TODO: Given an list of RSS feeds parse and process
TODO: Given an RSS feed parse and find new episodes, to add to download queue
TODO: Given a list of urls in a download queue, download and parse the files
- Create a basic queue list and process
- TODO: persists the queue to files to have history of downloads, this allows deleting mp3s after transcription

- Given a url, download the mp3 and transcribe
'''


# Data and Configuration
downloadPath = "/Users/alanrichardson/Downloads"
outputPath = "/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions"
outputFileName = "testpodcast-transcription"
whisperModel = "base"

csvCaches = outputPath
download_csv_cache = os.path.join(csvCaches, "download_queue.csv")
downloaded_csv_cache = os.path.join(csvCaches, "downloaded_items.csv")

download_queue = DownloadQueue(download_csv_cache, downloaded_csv_cache)
download_queue.add(DownloadFile("Test Podcast", "episode one", downloadPath, "https://downloads.pod.co/558da60d-be59-43be-afee-67c93f05c5e0/4c20f2bf-814a-47d3-90ca-42ede6325c2e.mp3"))
download_queue.add(DownloadFile("Test Podcast", "episode two", downloadPath, "https://downloads.pod.co/558da60d-be59-43be-afee-67c93f05c5e0/2c84ff05-8db6-4c4d-b975-24590b40ee54.mp3"))

next_download = download_queue.get_next()
# download and transcribe the next podcast
while next_download != None:
    #print(yaml.dump(download_queue, indent=2))

    inputAudioFile = download_if_not_exists(next_download.url, next_download.download_folder)

    transcribe(inputAudioFile, outputPath, outputFileName)

    download_queue.mark_as_downloaded(next_download)
    download_queue.save_caches()
    next_download = download_queue.get_next()


print("All Done")