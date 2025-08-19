# pyyaml just for printing for debugging convenience
import os
from podcastrss.RssFeed import RssFeed
from podcastrss.RssList import RssList

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
from routes.html import html_bp, set_rsslist
from routes.api import api_bp, define_rssList

app = Flask(__name__)


# Data and Configuration
print(os.name)
if os.name == 'nt':
    print("running on windows")
    downloadPath = "d:/downloads"
    outputPath = "d:/podcast-transcriptions"
else:
    print("running on mac?")
    # mac config - TODO: move to a config file and start app with config file name
    downloadPath = "/Users/alanrichardson/Downloads"
    outputPath = "/Users/alanrichardson/Documents/docs-git/dev/python/podcast-transcriptions"

outputFileName = "testpodcast-transcription"
whisperModel = "base"


rssList = RssList("podcasts")
rssList.set_config_path(os.path.join(outputPath, "podcasts-config"))
rssList.set_cache_path(outputPath)
rssList.set_download_path(downloadPath)
rssList.set_output_path(outputPath)

rssList.print_path_config()


# TODO: add a summary/description field for each podcast
# TODO: persist rssList to a file
# TODO: read from a file
# TODO: UI ability to read from a file
# TODO: eventually UI ability to add new and persist to file



# find a podcast rss feed https://castos.com/tools/find-podcast-rss-feed/
# find a podcast rss feed from apple podcast link https://www.labnol.org/podcast

# Testing podcasts
rssList.feeds.append(RssFeed("AB Testing", "https://anchor.fm/s/45580f58/podcast/rss", ["testing"], "https://www.moderntesting.org/", [], "2025 04 01 00:00:01 UTC", "AB Testing - Each episode is a chat between Brent Jensen and Alan Page with an occasional special guest."))
rssList.feeds.append(RssFeed("Applause Ready Test Go", "https://fast.wistia.com/channels/1b8462lt0q/rss", ["testing"], "https://www.applause.com/podcasts/", [], "2025 06 01 00:00:01 UTC", "Applause - Ready Test Go - Official podcast from Crowdtesting company Applause. The show notes have full episode descriptions and transcripts. Released as audio and video."))
rssList.feeds.append(RssFeed("MOT This Week in Testing","https://fast.wistia.com/channels/czgwdadw2c/rss", ["testing"], "https://www.ministryoftesting.com/podcasts", ["https://www.ministryoftesting.com"], "2025 06 01 00:00:01 UTC","MOT - This week in Testing - Varied hosts, group chat, often with community questions and involvement."))
rssList.feeds.append(RssFeed("Quality Blether","https://feeds.acast.com/public/shows/quality-blether", ["testing"], "https://shows.acast.com/quality-blether", [], "2025 01 01 00:00:01 UTC", "Quality Blether is the official podcast of the Scottish Testing Group. Episodes are guest interview based."))
rssList.feeds.append(RssFeed("Quality Remarks","https://www.spreaker.com/show/2507151/episodes/feed", ["testing"], "https://qualityremarks.com/", ["https://qualityremarks.com/qr-podcast/", "https://www.youtube.com/@KeithKlain"], "2025 06 01 00:00:01 UTC", "Quality Remarks is the podcast from Keith Klain. Each episode has a different guest. Recorded as audio and video."))
rssList.feeds.append(RssFeed("Quality Sense Podcast","https://feeds.soundcloud.com/users/soundcloud:users:815108872/sounds.rss", ["testing"], "https://abstracta.us/software-testing-podcast", ["https://www.youtube.com/playlist?list=PLquWeW1pThUEqpUW6o_KDhfcp7PXMMFW3"], "2025 04 01 00:00:01 UTC", "Quality Sense is a podcast from Testing Consultancy Abstracta. Released as audio and video."))
rssList.feeds.append(RssFeed("Quality Talks","https://anchor.fm/s/f6e76df4/podcast/rss", ["testing"], "https://qualitytalks.co.uk/podcast", ["https://www.youtube.com/@QualityTalksPodcast"], "2025 04 01 00:00:01 UTC", "Quality Talks is  Stu Day and Chris Henderson and different guest each episode. Released as audio and video. The official Show notes have summary, key points and time stamped chapters."))
rssList.feeds.append(RssFeed("Saucelabs Test Case Scenario","https://feeds.buzzsprout.com/2129346.rss", ["testing"], "https://www.youtube.com/@SauceLabs_Official/podcasts", [], "2025 04 01 00:00:01 UTC", "Saucelabs Test Case Scenario is an offical podcast from Saucelabs, usually with a different guest. Released as audio and video."))
rssList.feeds.append(RssFeed("Software Testing Unleashed","https://testing-unleashed.podigee.io/feed/mp3", ["testing"], "https://www.richard-seidl.com/en/testing-unleashed", ["https://www.youtube.com/playlist?list=PL48Mbm-L0hjB1OdwYi9h7jrq9t352-Zk_"], "2025 04 01 00:00:01 UTC", "Software Testing Unleashed - hosted by Richard Seidl. Different guest per episode. The official Show notes contain a comprehensive overview of the episode. Released as audio and video."))
# acast has each filename as media.mp3 TODO: use a local GUID as filename, which we allocate to each download URL (for now, if acast.com, delete after transcribing)
rssList.feeds.append(RssFeed("Tech and Test","https://feeds.buzzsprout.com/2313874.rss", ["testing"], "https://www.techandtest.co.uk/", ["https://www.youtube.com/@TechandTestPodcast","https://www.linkedin.com/company/tech-and-test-podcast/","https://www.linkedin.com/in/peterintest/",], "2025 01 01 00:00:01 UTC", "Tech and Test - hosted by Peter Johnson. Show notes has a summary of episode and resource links."))
rssList.feeds.append(RssFeed("Test Guild", "https://testtalks.libsyn.com/rss", ["testing"], "https://testguild.com/", ["https://testguild.com/podcasts/automation/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU1jqvx46esyr56BXtm1QEds", "https://www.youtube.com/@JoeColantonio"], "2025 06 01 00:00:01 UTC", "Test Guild - hosted by Joe Colantonio has main topic focus on Testing or Automating. Each episode has a different guest. Show notes have comprehensive links and usually a full transcript. Released as audio and video."))
rssList.feeds.append(RssFeed("Test Guild Devops Toolchain Podcast","https://testguildperf.libsyn.com/rss", ["testing"], "https://testguild.com/podcasts/performance/", ["https://testguild.com/podcasts/performance/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU3pQfcrQmDrGMbx3aNMnLnW"], "2025 06 01 00:00:01 UTC", "Test Guild Devops Toolchain Podcast - hosted by Joe Colantonio has a Dev Ops and Cloud focus. Each episode has a different guest. Show notes have comprehensive links and usually a full transcript. Released as audio and video."))
rssList.feeds.append(RssFeed("Test Guild News Show","https://testguildnews.libsyn.com/rss", ["testing"], "https://testguild.com/podcasts/news/", ["https://testguild.com/podcasts/news/", "https://www.youtube.com/playlist?list=PL9AgRtJkydU1WSjOuUkOeRFTDN5dPyL6u"], "2025 06 01 00:00:01 UTC", "Test Guild News Show hosted by Joe Colantonio has a round up of Software Testing Tool news and updates. Released as audio and video. Show notes have links to source of each news update."))
# Not updated since 2021
#rssList.feeds.append(RssFeed("Test Guild Security Testing Podcast","https://testguildsecure.libsyn.com/rss", ["testing"], "https://www.youtube.com/playlist?list=PL9AgRtJkydU3JzSZcwWxMwrrzg9SSGWwH", ["https://www.youtube.com/playlist?list=PL9AgRtJkydU3JzSZcwWxMwrrzg9SSGWwH"], "2025 06 01 00:00:01 UTC"))
rssList.feeds.append(RssFeed("Test Guild ZapTalk Podcast","https://feeds.buzzsprout.com/2426420.rss", ["testing"], "https://testguild.com/podcasts/zaptalk/", ["https://www.youtube.com/playlist?list=PL9AgRtJkydU1DWqrt1ilthObjql7zvPZ5"], "2025 04 01 00:00:01 UTC", "Test Guild ZapTalk - ZAPTEST sponsored podcast hosted by Joe Colantonio and Alex Zap. Often with a guest. Released as audio and video."))
rssList.feeds.append(RssFeed("Test and Code","https://feeds.transistor.fm/test-and-code", ["testing"], "https://testandcode.com/", ["https://testandcode.com/archive"], "2025 04 01 00:00:01 UTC", "Test and Code -  host Brian Okken. Mix of Python Automation and guest episodes. Official show notes have an overview and a transcript."))
rssList.feeds.append(RssFeed("The Engineering Quality Podcast", "https://anchor.fm/s/f6a276e0/podcast/rss", ["testing"], "https://www.engineeringqualitypodcast.com/", ["https://music.youtube.com/playlist?list=PLqUuvcBX10HyISlL5fhvGJosizW8PD9rV"], "2025 06 01 00:00:01 UTC", "The Engineering Quality Podcast - hosted by Alessandra Moreira, Royalee Martin, and Veronika Pliusnina. Testing focused panel discussions."))
rssList.feeds.append(RssFeed("The EvilTester Show", "https://feed.pod.co/the-evil-tester-show", ["testing"], "https://eviltester.com/show", ["https://eviltester.com"],"2020 01 01 00:00:01 UTC", "The Evil Tester Show - hosted by Alan Richardson. Occasional guest episodes. Show notes have comprehensive descriptions and resource links. Released as audio and video."))
rssList.feeds.append(RssFeed("The Testing Peers", "https://feeds.buzzsprout.com/1078751.rss", ["testing"], "https://testingpeers.com/", ["https://www.youtube.com/playlist?list=PLgToaFvlUC7mruBdL9eQDS3WFcpg9ooeI"], "2025 06 01 00:00:01 UTC", "The Testing Peers - panel discussions about testing. Usually Chris Armstrong, Simon Prior, Russell Craxford and David Maynard, with occasional special guests. Show notes on the website have an episode description and resource links."))
rssList.feeds.append(RssFeed("The Testing Show", "https://thetestingshow.libsyn.com/rss", ["testing"], "https://www.qualitestgroup.com/insights/podcasts/", [], "2025 06 01 00:00:01 UTC", "The Testing Show - Qualitest panel discussions with guests. Main hosts Matthew Heusser and Michael Larsen. Official show notes have a short summary but the web page for each episode has a transcript."))
rssList.feeds.append(RssFeed("The Vernon Richard Show", "https://feeds.transistor.fm/the-vernon-richard-show", ["testing"], "https://thevernonrichardshow.com/", ["https://www.youtube.com/@TheVernonRichardShow"], "2025 06 01 00:00:01 UTC", "The Vernon Richard Show - hosted by Vernon Richards and Richard Bradshaw. Usually a Testing themed discussion between Vernon and Richard. Official show notes have summary description, timestamped chapter headings, resource links. Show notes on the website sometimes have a full transcript. Released as audio and video."))

# practitest The Test Management Mindset seem to be audio generated by NotebookLM so will not include
# https://www.youtube.com/playlist?list=PLg74w4qP0mfF27a5pGDgGf691jrRlfMzc
# https://open.spotify.com/show/7JKJZVMxo6xdYeRm4RCgod?si=c7f43a090849403e&nd=1&dlsi=471dd808fe594c78

# Development

#
rssList.feeds.append(RssFeed("Podcasts by InfoQ", "https://feeds.soundcloud.com/users/soundcloud:users:215740450/sounds.rss", ["development"], "https://www.infoq.com/podcasts/", ["https://www.youtube.com/playlist?list=PLndbWGuLoHeZLVC9vl0LzLvMWHzpzIpir"], "2025 06 01 00:00:01 UTC", "Guest focussed episodes on general development topics. Show notes for each episode have summaries and transcripts. Released as audio and video."))

rssList.feeds.append(RssFeed("Engineering Culture by InfoQ", "https://feeds.soundcloud.com/users/soundcloud:users:258266127/sounds.rss", ["development"], "https://www.infoq.com/podcasts/", ["https://www.youtube.com/playlist?list=PLndbWGuLoHeYaFgbuLnvO5Qab2pFBaSWX"], "2025 06 01 00:00:01 UTC", "Guest focussed episodes on general development topics. Show notes for each episode have summaries and transcripts. Released as audio and video."))

# AI
rssList.feeds.append(RssFeed("MLOps.community","https://anchor.fm/s/174cb1b8/podcast/rss",["ai"], "https://mlops.community/", ["https://www.youtube.com/@MLOps"], "2025 06 01 00:00:01 UTC"))
# Business

rssList.feeds.append(RssFeed("Technovation","https://www.metisstrategy.com/interview/feed/podcast/",["business"], "https://www.metisstrategy.com/podcast-overview/", ["https://www.youtube.com/playlist?list=PLo67eg0gOxoDzmwXgoITSDVSgMoJxkXH3"], "2025 01 01 00:00:01 UTC"))
rssList.feeds.append(RssFeed("Build Your Edge","https://api.riverside.fm/hosting/kootpfl4.rss",["business"], "https://www.buildyouredge.org", ["https://www.youtube.com/watch?v=9PFufge1Xvg","https://buildyouredge.substack.com/", "https://www.buildyouredge.org/downloads"], "2025 08 01 00:00:01 UTC", "Build Your Edge is a motivational business podcast hosted by Jeremy Burns. Released as audio and video. Main site page for episode has downloadable resources."))
# rssList.feeds.append(RssFeed("The 505 Podcast","https://feeds.redcircle.com/7e1027d2-d8b5-4f66-882b-03422b443282",["business"], "https://www.youtube.com/@the505podcast", [], "2025 05 01 00:00:01 UTC", "A strategy modern business podcast. Released as audio and video."))


# Marketing
rssList.feeds.append(RssFeed("Fastlane Founders","https://fastlanefounders.com/feed/podcast/",["marketing"], "https://fastlanefounders.com/", [], "2025 01 01 00:00:01 UTC"))
# Development
rssList.feeds.append(RssFeed("Goto tech","https://feeds.buzzsprout.com/1714721.rss",["development"], "https://gotopia.tech/", ["https://www.youtube.com/playlist?list=PLEx5khR4g7PLXTa3BfyST9-BSIjkvQ7ka"], "2025 07 01 00:00:01 UTC"))


# TODO: after config - to allow youtube to be in different config files
# youtube - https://www.youtube.com/feeds/videos.xml?channel_id=YOUR_CHANNEL_ID
# to find channelid - goto channel page, share channel, copy id
# https://www.youtube.com/feeds/videos.xml?channel_id=UCCAwIFH3FRVD9GBuVRW_mUw
# https://www.youtube.com/@eviltester
# could delegate to yt-dlp for the heavy lifting of downloading, converting to mp3, and then use normal process
# or could delegate to MarkItDown and just get the markdown version of the YT video https://github.com/microsoft/markitdown
# 20250810 - tried markitdown and it failed on mp3 and youtube

#rssList.feeds.append(RssFeed("EvilTester Videos - Youtube","https://www.youtube.com/feeds/videos.xml?channel_id=UCCAwIFH3FRVD9GBuVRW_mUw",["youtube"], "https://www.youtube.com/@eviltester", [], "2025 07 01 00:00:01 UTC"))

# TODO: persist the path config and the name in the config file and re-load that as well
# save the feeds - temporarily and load to check
# feeds_config_path = os.getcwd()
# feeds_file_path = os.path.join(feeds_config_path,"feeds_config.json")
# rssList.save_feeds_to_json(feeds_file_path)
# rssList = RssList("podcasts")
# rssList.set_config_path(os.path.join(outputPath, "podcasts-config"))
# rssList.set_cache_path(outputPath)
# rssList.set_download_path(downloadPath)
# rssList.set_output_path(outputPath)
# rssList.load_feeds_from_json(feeds_file_path)


print("\n")



# API config
define_rssList(rssList)

# HTML endpoints config
set_rsslist(rssList)


# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(html_bp, url_prefix='')

if __name__ == "__main__":
    print("http://localhost:5000")
    app.run(debug=True)