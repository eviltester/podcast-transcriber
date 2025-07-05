# pyyaml just for printing for debugging convenience
import yaml
import os
from downloads import DownloadFile, DownloadQueue, download_if_not_exists, filenameify
from rss import RssFeed, RssListReader
from transcriber import Transcriber
from summarization import SummarizeQueue, SummarizeFile, summarize

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
TODO: output all meta data from the RSS file into the episode folders e.g. episode number, length, etc.
TODO: show the meta data in the summary output
TODO: create a DB or CSV with all details rather than multiple csv
- use the utils and the built in output to text, srt, vtt options
TODO: investigate if passing in language as english is faster or if using base.en is faster
TODO: ui
- TODO: create a ui
- TODO: allow repeat - download, transcripte, summarize
- TODO: configure summarization with custom prompts and models
- TODO: Rss config - download all or 'after date X' - to avoid getting old episodes when subscribe
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
summarize_queue_csv_cache = os.path.join(csvCaches, "summarize_queue.csv")
summarized_csv_cache = os.path.join(csvCaches, "summarized_items.csv")

print("----")
print("CONFIG:")
print("Download Path: " + downloadPath)
print("Output Path: " + outputPath)
print("----")


# TODO: create a Podcast class and a PodcastEpisode class
# find a podcast rss feed https://castos.com/tools/find-podcast-rss-feed/
# find a podcast rss feed from apple podcast link https://www.labnol.org/podcast
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
    # TODO: add a category attribute
    # Testing podcasts
    rssList.feeds.append(RssFeed("The EvilTester Show", "https://feed.pod.co/the-evil-tester-show"))
    rssList.feeds.append(RssFeed("The Testing Peers", "https://feeds.buzzsprout.com/1078751.rss"))
    rssList.feeds.append(RssFeed("AB Testing", "https://anchor.fm/s/45580f58/podcast/rss"))
    rssList.feeds.append(RssFeed("Test Guild", "https://testtalks.libsyn.com/rss"))
    rssList.feeds.append(RssFeed("The Vernon Richard Show", "https://feeds.transistor.fm/the-vernon-richard-show"))
    rssList.feeds.append(RssFeed("The Testing Show", "https://thetestingshow.libsyn.com/rss"))
    rssList.feeds.append(RssFeed("The Engineering Quality Podcast", "https://anchor.fm/s/f6a276e0/podcast/rss"))
    rssList.feeds.append(RssFeed("Applause Ready Test Go", "https://fast.wistia.com/channels/1b8462lt0q/rss"))
    rssList.feeds.append(RssFeed("Quality Remarks","https://www.spreaker.com/show/2507151/episodes/feed"))
    # AI
    rssList.feeds.append(RssFeed("MLOps.community","https://anchor.fm/s/174cb1b8/podcast/rss"))


# Scan for new episodes and add to download queue
download_queue = DownloadQueue(download_csv_cache, downloaded_csv_cache)


summarize_queue = SummarizeQueue(summarize_queue_csv_cache, summarized_csv_cache)

# def fixFileNameScrewup(filename):
#     lastFileNameLen = -1
#     fileNameToUse = filename
#     while lastFileNameLen != len(fileNameToUse):
#         lastFileNameLen = len(fileNameToUse)
#         #fileNameToUse = fileNameToUse.replace("b-","")
#         #fileNameToUse = fileNameToUse.replace("--","")
#     return fileNameToUse

# hack to fill the caches with currently downloaded items
# for downloadedItem in download_queue.downloaded:
#     print(downloadedItem.podcast_name)
#     filename = filenameify(downloadedItem.episode_title)
#     fixedfoldername = fixFileNameScrewup(filename)
#     # calculate the filename here
#     outputFilePath = os.path.join(outputPath, filenameify(downloadedItem.podcast_name),fixedfoldername, fixedfoldername + "-base.para.md" )
#     # check if file exists
#     if not os.path.exists(outputFilePath):
#         print("Transcript not exist: " + outputFilePath)
#         # try the other path
#         outputFilePath = os.path.join(outputPath, filenameify(downloadedItem.podcast_name),fixedfoldername, fixedfoldername + "-base.para.txt.md" )
#         if os.path.exists(outputFilePath):
#             summarize_queue.add(SummarizeFile(downloadedItem.podcast_name, fixedfoldername, outputFilePath))
#             summarize_queue.save_caches()
#         else:
#             exit()
#     else:
#         print(outputFilePath)
#         summarize_queue.add(SummarizeFile(downloadedItem.podcast_name, fixedfoldername, outputFilePath))
#         summarize_queue.save_caches()


for rss_feed in rssList.feeds:
    rss_feed.load()

    rss_feed.load_seen_cache(outputPath)
    rss_feed.find_new_rss_items()
    for item in rss_feed.new_items:
        print (item.title + " - " + item.download_url)

        # add new items to download queue
        for item in rss_feed.new_items:
            download_queue.add(DownloadFile(item.feedname, item.title, downloadPath, item.download_url))
            rss_feed.add_to_seen_cache(item)

        # write rss cache file
        download_queue.save_caches()
        rss_feed.write_seen_cache(outputPath)

next_download = download_queue.get_next()

transcriber = Transcriber()


# work through the summarization queue
# summarization works but requires fine tuning
next_summary = summarize_queue.get_next()
while next_summary != None:
    # TODO: pass in the basic meta data - podcast title, name, links etc.
    summarize(next_summary.file)
    summarize_queue.mark_as_done(next_summary)
    summarize_queue.save_caches()
    next_summary = summarize_queue.get_next()



# download and transcribe the next podcast
while next_download != None:
    #print(yaml.dump(download_queue, indent=2))

    # TODO: if there is an error downloading then add to an error queue
    print("Processing: ", next_download.podcast_name, " - ", next_download.episode_title)

    inputAudioFile = download_if_not_exists(next_download.url, downloadPath)

    transcriptionFileName = filenameify(next_download.episode_title)
    transcriptionOutputFolderName = filenameify(next_download.podcast_name)
    transcriptionOutputFolder = os.path.join(outputPath, transcriptionOutputFolderName)
    if not os.path.exists(transcriptionOutputFolder):
        os.makedirs(transcriptionOutputFolder)

    # TODO: if there is an error here add it to an error queue
    fileToSummarize = transcriber.transcribe(inputAudioFile, transcriptionOutputFolder, transcriptionFileName)

    # now that it is transcribed, add it to the summary queue
    if fileToSummarize != "":
        summarize_queue.add(SummarizeFile(next_download.podcast_name, next_download.episode_title, fileToSummarize))
        summarize_queue.save_caches()

    download_queue.mark_as_downloaded(next_download)
    download_queue.save_caches()
    next_download = download_queue.get_next()

# summarize



print("All Done")