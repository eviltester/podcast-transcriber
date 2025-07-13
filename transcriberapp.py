# pyyaml just for printing for debugging convenience
import yaml
import os

from download_transcribe_processor import DownloadAndTranscribeProcessor
from downloads import DownloadFile, DownloadQueue, download_if_not_exists, filenameify
from markdownReporter import generateMarkdownSummaryReport
from rss import RssFeed, RssListReader
from rss_feed_scanner import RssFeedScanner
from summarization import SummarizeQueue, SummarizeFile, summarize
from summarize_queue_processor import SummarizeQueueProcessor

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
- output all meta data from the RSS file into the episode folders e.g. episode number, length, etc.
- show the meta data in the summary output
TODO: output summaries as JSON and convert to markdown at export report time
TODO: create a DB or CSV with all details rather than multiple csv
- use the utils and the built in output to text, srt, vtt options
TODO: investigate if passing in language as english is faster or if using base.en is faster
TODO: ui
- TODO: create a ui
- TODO: allow repeat - download, transcripte, summarize, editing
- TODO: allow experimenting with different prompts and models
- TODO: configure summarization with custom prompts and models
- Rss config - download all or 'after date X' - to avoid getting old episodes when subscribe
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


# TODO: podcast.csv should be a podcast.yaml to allow expanding with new fields and support arrays for links and categories
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

    # Testing podcasts
    rssList.feeds.append(RssFeed("The EvilTester Show", "https://feed.pod.co/the-evil-tester-show", ["testing"], "https://eviltester.com/show", ["https://eviltester.com"]))
    rssList.feeds.append(RssFeed("The Testing Peers", "https://feeds.buzzsprout.com/1078751.rss", ["testing"], "https://testingpeers.com/", [], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("AB Testing", "https://anchor.fm/s/45580f58/podcast/rss", ["testing"], "https://www.moderntesting.org/", [], "2025 04 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("Test Guild", "https://testtalks.libsyn.com/rss", ["testing"], "https://testguild.com/", ["https://testguild.com/podcasts/automation/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU1jqvx46esyr56BXtm1QEds", "https://www.youtube.com/@JoeColantonio", "2025 06 01 00:00:01 UTC"]))
    rssList.feeds.append(RssFeed("Test Guild News Show","https://testguildnews.libsyn.com/rss", ["testing"], "https://testguild.com/podcasts/news/", ["https://testguild.com/podcasts/news/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU1WSjOuUkOeRFTDN5dPyL6u"], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Test Guild Devops Toolchain Podcast","https://testguildperf.libsyn.com/rss", ["testing"], "https://testguild.com/podcasts/performance/", ["https://testguild.com/podcasts/performance/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU3pQfcrQmDrGMbx3aNMnLnW"], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Test Guild Security Testing Podcast","https://testguildsecure.libsyn.com/rss", ["testing"], "https://www.youtube.com/playlist?list=PL9AgRtJkydU3JzSZcwWxMwrrzg9SSGWwH", ["https://www.youtube.com/playlist?list=PL9AgRtJkydU3JzSZcwWxMwrrzg9SSGWwH"], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Test Guild ZapTalk Podcast","https://feeds.buzzsprout.com/2426420.rss", ["testing"], "https://testguild.com/podcasts/zaptalk/", ["https://www.youtube.com/playlist?list=PL9AgRtJkydU1DWqrt1ilthObjql7zvPZ5"], "2025 04 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("Software Testing Unleashed","https://testing-unleashed.podigee.io/feed/mp3", ["testing"], "https://www.richard-seidl.com/en/testing-unleashed", ["https://www.youtube.com/playlist?list=PL48Mbm-L0hjB1OdwYi9h7jrq9t352-Zk_"], "2025 04 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("Quality Sense Podcast","https://feeds.soundcloud.com/users/soundcloud:users:815108872/sounds.rss", ["testing"], "https://abstracta.us/software-testing-podcast", ["https://www.youtube.com/playlist?list=PLquWeW1pThUEqpUW6o_KDhfcp7PXMMFW3"], "2025 04 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("The Vernon Richard Show", "https://feeds.transistor.fm/the-vernon-richard-show", ["testing"], "https://thevernonrichardshow.com/", ["https://www.youtube.com/@TheVernonRichardShow"], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("The Testing Show", "https://thetestingshow.libsyn.com/rss", ["testing"], "https://www.qualitestgroup.com/insights/podcasts/", [], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("The Engineering Quality Podcast", "https://anchor.fm/s/f6a276e0/podcast/rss", ["testing"], "https://www.engineeringqualitypodcast.com/", [], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Applause Ready Test Go", "https://fast.wistia.com/channels/1b8462lt0q/rss", ["testing"], "https://www.applause.com/podcasts/", [], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Quality Remarks","https://www.spreaker.com/show/2507151/episodes/feed", ["testing"], "https://qualityremarks.com/", ["https://qualityremarks.com/qr-podcast/", "https://www.youtube.com/@KeithKlain"], "2025 06 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Test and Code","https://feeds.transistor.fm/test-and-code", ["testing"], "https://testandcode.com/", ["https://testandcode.com/archive"], "2025 04 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("MOT This Week in Testing","https://fast.wistia.com/channels/czgwdadw2c/rss", ["testing"], "https://www.ministryoftesting.com/podcasts", ["https://www.ministryoftesting.com"], "2025 06 01 00:00:01 UTC"))

# AI
    rssList.feeds.append(RssFeed("MLOps.community","https://anchor.fm/s/174cb1b8/podcast/rss",["ai"], "https://mlops.community/", ["https://www.youtube.com/@MLOps"], "2025 06 01 00:00:01 UTC"))

print("\n")

# todo add a command line argument to skip and start batch queue process
x = input('Enter to start batch queue process:')

if x == "":
    # Scan for new episodes and add to download queue
    download_queue = DownloadQueue(download_csv_cache, downloaded_csv_cache)

    # get the summarize queue
    summarize_queue = SummarizeQueue(summarize_queue_csv_cache, summarized_csv_cache)

    feed_scanner = RssFeedScanner(outputPath, download_queue, rssList, downloadPath)
    feed_scanner.scan_for_new_podcasts()

    download_queue_processor = DownloadAndTranscribeProcessor(download_queue, summarize_queue, downloadPath, outputPath)
    download_queue_processor.download_transcribe_and_queue_for_summarization()

    summarize_processor = SummarizeQueueProcessor(summarize_queue, outputPath)
    summarize_processor.summarize_all()


    print("All Done")


# else show a UI