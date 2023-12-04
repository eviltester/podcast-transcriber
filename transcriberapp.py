# pyyaml just for printing for debugging convenience
import yaml
import os
from downloads import DownloadFile, DownloadQueue, download_if_not_exists, filenameify
from rss import RssFeed, RssListReader
from transcriber import Transcriber

#
# Main App code
#


'''
Todo List
TODO: configurable delete downloaded files after transcription (keep reference in downloaded queue)
TODO: command line args to override config files and defaults
TODO: config files to configure and override defaults
TODO: separate parse and download into separate processes (transcription queue separate from download queue)
TODO: separate parse and download into separate actions
- download files into podcast named folders
TODO: allow start and stopping mid process
TODO: Create a transcription queue and transcribed queue
TODO: pick up queue items and start from queues
- output the files to episode folders
TODO: output more meta data from the RSS file into the episode folders e.g. episode number, length, etc.
- use the utils and the built in output to text, srt, vtt options
TODO: investigate if passing in language as english is faster or if using base.en is faster
- Given a list of RSS feeds parse and process
- Given an RSS feed parse and find new episodes, to add to download queue
   - download and parse rss feed
   - create a cache for each rss feed of the items 'seen' in the previous rss feed
   - add transcriptions into podcast named folders
   - add model name used to create transcript into files
- Given a list of urls in a download queue, download and parse the files
   - Create a basic queue list and process
   - Persists the queue to files to have history of downloads, this allows deleting mp3s after transcription
- Given a url, download the mp3 and transcribe
TODO: try https://github.com/huggingface/distil-whisper
'''

# Data and Configuration
print(os.name)
if os.name == 'nt':
    print("running on windows")
    downloadPath = "d:/downloads"
    outputPath = "d:/git/dev/python/podcast-transcriptions"
else:
    print("running on mac?")
    # mac config - TODO: move to a config file and start app with config file name
    downloadPath = "/Users/alanrichardson/Downloads"
    outputPath = "/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions"

outputFileName = "testpodcast-transcription"
whisperModel = "base"

csvCaches = outputPath
download_csv_cache = os.path.join(csvCaches, "download_queue.csv")
downloaded_csv_cache = os.path.join(csvCaches, "downloaded_items.csv")

print("----")
print("CONFIG:")
print("Download Path: " + downloadPath)
print("Output Path: " + outputPath)
print("----")


# TODO: create a Podcast class and a PodcastEpisode class

#Add a file called podcasts.csv in the current folder with the list of podcasts to load
# e.g.
'''
"The EvilTester Show","https://feed.pod.co/the-evil-tester-show"
"The Testing Peers","https://feeds.buzzsprout.com/1078751.rss"
"AB Testing","https://anchor.fm/s/45580f58/podcast/rss"
'''
defaultPodcastsCSV = os.path.join(os.getcwd(),"podcasts.csv")
rssList = RssListReader(defaultPodcastsCSV)
if(os.path.exists(defaultPodcastsCSV)):
    rssList.loadFeeds()
else:
    # add some defaults
    print("Could not find a podcasts.csv file in current directory, create one and add some podcasts to download")
    print("e.g.")
    print("The EvilTester Show,https://feed.pod.co/the-evil-tester-show")
    print("The Testing Peers,https://feeds.buzzsprout.com/1078751.rss")
    rssList.feeds.append(RssFeed("The EvilTester Show", "https://feed.pod.co/the-evil-tester-show"))
    rssList.feeds.append(RssFeed("The Testing Peers", "https://feeds.buzzsprout.com/1078751.rss"))
    rssList.feeds.append(RssFeed("AB Testing", "https://anchor.fm/s/45580f58/podcast/rss"))

# Scan for new episodes and add to download queue
download_queue = DownloadQueue(download_csv_cache, downloaded_csv_cache)

for rss_feed in rssList.feeds:
    rss_feed.load()

    rss_feed.load_seen_cache(outputPath)
    rss_feed.find_new_rss_items()
    for item in rss_feed.new_items:
        print (item.title + " - " + item.download_url)

        # add new items to download queue
        for item in rss_feed.new_items:
            download_queue.add(DownloadFile(item.feedname, item.title, downloadPath, item.download_url))
            rss_feed.seen_items.append(item)

        # write rss cache file
        download_queue.save_caches()
        rss_feed.write_seen_cache(outputPath)

next_download = download_queue.get_next()

transcriber = Transcriber()

# download and transcribe the next podcast
while next_download != None:
    #print(yaml.dump(download_queue, indent=2))

    inputAudioFile = download_if_not_exists(next_download.url, downloadPath)

    transcriptionFileName = filenameify(next_download.episode_title)
    transcriptionOutputFolderName = filenameify(next_download.podcast_name)
    transcriptionOutputFolder = os.path.join(outputPath, transcriptionOutputFolderName)
    if not os.path.exists(transcriptionOutputFolder):
        os.makedirs(transcriptionOutputFolder)
    transcriber.transcribe(inputAudioFile, transcriptionOutputFolder, transcriptionFileName)

    download_queue.mark_as_downloaded(next_download)
    download_queue.save_caches()
    next_download = download_queue.get_next()


print("All Done")