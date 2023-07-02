import os
from downloads import download_if_not_exists
from transcriber import transcribe

#
# Main App code
#


'''
Todo List
TODO: Given an list of RSS feeds parse and process
TODO: Given an RSS feed parse and find new episodes, to add to download queue
TODO: Given a list of urls in a download queue, download and parse the files
- TODO: Create a basic queue list and process
- TODO: persists the queue to files to have history of downloads, this allows deleting mp3s after transcription

- Given a url, download the mp3 and transcribe
'''


# Data and Configuration
downloadUrl="https://downloads.pod.co/558da60d-be59-43be-afee-67c93f05c5e0/4c20f2bf-814a-47d3-90ca-42ede6325c2e.mp3"
downloadPath = "/Users/alanrichardson/Downloads"
outputPath = "/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions"
outputFileName = "testpodcast-transcription"
whisperModel = "base"



# download the next podcast
inputAudioFile = download_if_not_exists(downloadUrl, downloadPath)

transcribe(inputAudioFile, outputPath, outputFileName)


print("All Done")