# pyyaml just for printing for debugging convenience
import os
from rss import RssFeed, RssListReader


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
- TODO: allow repeat - download, transcript, summarize, editing
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

from flask import Flask
from routes.html import html_bp, set_feeds_list, set_output_report_path, output_path, set_podcast_folders_path, \
    set_cache_files
from routes.api import api_bp, define_cache_files, define_paths, define_rssList

app = Flask(__name__)


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

    # Testing podcasts
    rssList.feeds.append(RssFeed("The EvilTester Show", "https://feed.pod.co/the-evil-tester-show", ["testing"], "https://eviltester.com/show", ["https://eviltester.com"]))
    rssList.feeds.append(RssFeed("The Testing Peers", "https://feeds.buzzsprout.com/1078751.rss", ["testing"], "https://testingpeers.com/", ["https://www.youtube.com/playlist?list=PLgToaFvlUC7mruBdL9eQDS3WFcpg9ooeI"], "2025 06 01 00:00:01 UTC"))
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

    # acast has each filename as media.mp3 TODO: use a local GUID as filename, which we allocate to each download URL (for now, if acast.com, delete after transcribing)
    rssList.feeds.append(RssFeed("Quality Blather","https://feeds.acast.com/public/shows/quality-blether", ["testing"], "https://shows.acast.com/quality-blether", [], "2025 01 01 00:00:01 UTC"))
    rssList.feeds.append(RssFeed("Tech and Test","https://feeds.buzzsprout.com/2313874.rss", ["testing"], "https://www.techandtest.co.uk/", ["https://www.youtube.com/@TechandTestPodcast","https://www.linkedin.com/company/tech-and-test-podcast/","https://www.linkedin.com/in/peterintest/",], "2025 01 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("Quality Talks","https://anchor.fm/s/f6e76df4/podcast/rss", ["testing"], "https://qualitytalks.co.uk/podcast", ["https://www.youtube.com/@QualityTalksPodcast"], "2025 04 01 00:00:01 UTC"))

    rssList.feeds.append(RssFeed("Saucelabs Test Case Scenario","https://feeds.buzzsprout.com/2129346.rss", ["testing"], "https://www.youtube.com/@SauceLabs_Official/podcasts", [], "2025 04 01 00:00:01 UTC"))


    # practitest The Test Management Mindset seem to be audio generated by NotebookLM so will not include
    # https://www.youtube.com/playlist?list=PLg74w4qP0mfF27a5pGDgGf691jrRlfMzc
    # https://open.spotify.com/show/7JKJZVMxo6xdYeRm4RCgod?si=c7f43a090849403e&nd=1&dlsi=471dd808fe594c78

# AI
    rssList.feeds.append(RssFeed("MLOps.community","https://anchor.fm/s/174cb1b8/podcast/rss",["ai"], "https://mlops.community/", ["https://www.youtube.com/@MLOps"], "2025 06 01 00:00:01 UTC"))
# Business
    rssList.feeds.append(RssFeed("Technovation","https://www.metisstrategy.com/interview/feed/podcast/",["business"], "https://www.metisstrategy.com/podcast-overview/", ["https://www.youtube.com/playlist?list=PLo67eg0gOxoDzmwXgoITSDVSgMoJxkXH3"], "2025 01 01 00:00:01 UTC"))
# Marketing
    rssList.feeds.append(RssFeed("Fastlane Founders","https://fastlanefounders.com/feed/podcast/",["marketing"], "https://fastlanefounders.com/", [], "2025 01 01 00:00:01 UTC"))




print("\n")



# API config
define_cache_files(download_csv_cache, downloaded_csv_cache, summarize_queue_csv_cache, summarized_csv_cache)
define_paths(downloadPath, outputPath)
define_rssList(rssList)

# HTML endpoints config
set_feeds_list(rssList.feeds)
set_output_report_path(os.path.join(outputPath, "output-reports"))
set_podcast_folders_path(outputPath)
set_cache_files(download_csv_cache, downloaded_csv_cache, summarize_queue_csv_cache, summarized_csv_cache)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(html_bp, url_prefix='')

if __name__ == "__main__":
    print("http://localhost:5000")
    app.run(debug=True)