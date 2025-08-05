import csv
import os

import feedparser
from os import path
from unicodedata import normalize
from dateutil.parser import parse

from downloads import filenameify
from podcast_episode import PodcastEpisode

from html.parser import HTMLParser
from markdownify import markdownify as md

from podcast_episode import load_the_podcast_episode_data, store_the_podcast_episode_data

class HtmlTagRemover(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, data):
        self.result.append(data)

    def get_data(self):
        return ''.join(self.result)

class RssList:
    def __init__(self, name):
        self.name = name
        self.feeds = []
        self.config_path = None
        self.cache_path = None
        self.download_path = None
        self.output_path = None

        # main queues
        self.download_csv_cache = None
        self.downloaded_csv_cache = None
        self.summarize_queue_csv_cache = None
        self.summarized_csv_cache = None

    def set_config_path(self, config_path):
        self.config_path = config_path

    def set_cache_path(self, cache_path):
        self.cache_path = cache_path
        self.download_csv_cache = os.path.join(cache_path, "download_queue.csv")
        self.downloaded_csv_cache = os.path.join(cache_path, "downloaded_items.csv")
        self.summarize_queue_csv_cache = os.path.join(cache_path, "summarize_queue.csv")
        self.summarized_csv_cache = os.path.join(cache_path, "summarized_items.csv")

    def set_download_path(self, download_path):
        self.download_path = download_path

    def set_output_path(self, output_path):
        self.output_path = output_path

    def print_path_config(self):
        print("----")
        print(f"CONFIG: {self.name}")
        print(f"**UNUSED** Config Path: {self.config_path}")
        print(f"Download Path: {self.download_path}")
        print(f"Output Path: {self.output_path}")
        print(f"Cache Path: {self.cache_path}")
        print("----")

    def get_podcast_details(self, podcast_name):
        if self.feeds is not None:
            for podcast in self.feeds:
                if podcast_name == podcast.feedname or podcast_name == filenameify(podcast.feedname):
                    return podcast
        return None

    def get_category_names(self):
        categories_set = set([])
        if self.feeds is not None:
            for podcast in self.feeds:
                for a_category in podcast.categories:
                    categories_set.add(a_category)

        return sorted(list(categories_set))

class RssListReader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.feeds = []

    # todo: load and save needs to include all fields in the RssFeed
    def loadFeeds(self):
        with open(self.filepath, newline='') as csvfile:
            rss_list_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in rss_list_reader:
                self.feeds.append(RssFeed(feedname = row[0], feed_rss_url=row[1]))


class RssFeed:
    def __init__(self, feedname, feed_rss_url, categories=None, homeUrl="", hrefs=None, earliestAutoDownloadDate=None, description=""):
        self.feedname =  normalize('NFD', feedname).encode('ascii','ignore').decode('utf-8')
        self.feed_rss_url = feed_rss_url
        self.parsed_feed = None
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        self.homeUrl = homeUrl
        if hrefs is None:
            hrefs = []
        else:
            self.hrefs = hrefs
        # earliest date that auto download should start from
        self.earliestAutoDownloadDate = earliestAutoDownloadDate

        self.new_podcast_episodes = []
        self.seen_podcast_episodes = []
        self.seen_urls = set()
        self.new_urls = set()
        self.cache_path = ""
        self.url_safe_feedname = filenameify(feedname)
        self.description = description

    def add_to_seen_cache(self, anItem):
        if(anItem.download_url in self.seen_urls):
            print("Removing duplicate from seen cache", anItem.download_url)
        else:
            self.seen_urls.add(anItem.download_url)
            self.seen_podcast_episodes.append(anItem)


    def load(self):
        # https://pypi.org/project/feedparser/
        self.parsed_feed = feedparser.parse(self.feed_rss_url)

    def __cached_file_name(self):
        cache_file_name = filenameify(self.feedname)
        cache_file_name = cache_file_name + ".rss-seen.csv"
        return cache_file_name
    
    def load_seen_cache(self, cache_folder_path):        

        self.cache_path = cache_folder_path
        filepath = path.join(cache_folder_path,self.__cached_file_name())
        if(not path.exists(filepath)):
            return

        with open(filepath, newline='') as csvfile:
            rss_list_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in rss_list_reader:
                if(row[3] in self.seen_urls):
                    print("Removing duplicate from seen cache", row[1])
                else:
                    self.seen_urls.add(row[3])
                    # feedname = row[0], title=row[1], show_notes_url=row[2], download_url=row[3])
                    episode = load_the_podcast_episode_data(cache_folder_path, row[0], row[1])
                    self.seen_podcast_episodes.append(episode)

    def find_new_rss_items(self):

        print("scanning rss feed " + self.feedname)

        if(self.parsed_feed==None):
            print("feed not loaded")

        # base newness on "have I seen this download url" before?
        for item in self.parsed_feed.entries:

            possibleNewEpisode = self.rss_item_to_PodcastEpisode(self.feedname,item)
            #store_the_podcast_episode_data(self.cache_path,possibleNewEpisode)

            seen_before = False
            for seen in self.seen_podcast_episodes:
                if(seen.download_url == possibleNewEpisode.download_url):
                    print(".", end='')
                    #print("seen episode before " + item.title)
                    seen_before = True
                    break

            if(not seen_before):
                if(possibleNewEpisode.download_url in self.new_urls):
                    print("not adding duplicate new item ", item.title)
                else:
                    self.new_urls.add(possibleNewEpisode.download_url)
                    self.new_podcast_episodes.append(possibleNewEpisode)
                    store_the_podcast_episode_data(self.cache_path,possibleNewEpisode)

    def rss_item_to_PodcastEpisode(self, podcastName, rssItem):

        download_url = ""
        for aLink in rssItem.links:
            if(aLink.type=="audio/mpeg" or aLink.type=="audio/x-m4a" or aLink.type.startswith("audio/")):
                download_url = aLink.href
            if(download_url==""):
                #print("error parsing rss feed cannot find download url for item " + rssItem.title + " - " + rssItem.link)
                # try to find in enclosure
                for anEnclosure in rssItem.enclosures:
                    if(anEnclosure.type=="audio/mpeg" or anEnclosure.type=="audio/x-m4a" or anEnclosure.type.startswith("audio/")):
                        if(hasattr(anEnclosure, "href")):
                            download_url = anEnclosure.href
                        if(download_url=="" and hasattr(anEnclosure, "url")):
                            download_url = anEnclosure.url

        show_notes_link = ""
        if(hasattr(rssItem, "link")):
            show_notes_link = rssItem.link

        publishedDate = parse(rssItem.get("published",None))

        duration = rssItem.get("itunes_duration", "00:00:00")

        episode_title = rssItem.get("itunes_title", rssItem.get("title", None))
        if episode_title == None:
            if hasattr(rssItem,"title_detail"):
                episode_title = rssItem["title_detail"].get("value","Unknown")

        author = rssItem.get("author", None)
        if author == None:
            if hasattr(rssItem,"author_detail"):
                author = rssItem["author_detail"].get("name",None)
            if author == None:
                if hasattr(rssItem,"authors"):
                    author = ""
                    authors = rssItem["authors"]
                    postfix = ""
                    for anAuthor in authors:
                        author = author + postfix + anAuthor
                        postfix = ", "
                else:
                    author = "Unknown"

        summary = rssItem.get("summary", None)
        if summary == None:
            if hasattr(rssItem, "summary_detail"):
                summary = rssItem["summary_detail"].get("value","")

        # todo might also be in content[0].value, might also be in subtitle or subtitle_detail
        # htmlTagRemover = HtmlTagRemover()
        # htmlTagRemover.feed(summary)
        # summary = htmlTagRemover.get_data()
        # convert summary to markdown rather than stripping html tags
        summary = md(summary)

        additionalLinks = {}
        if hasattr(rssItem,"links"):
            for additionalLink in rssItem.links:
                additionalLinks.update({additionalLink.get("rel","a_") + "_" + additionalLink.get("type", "_x"): additionalLink.get("href","")})

        imageUrl = ""
        if hasattr(rssItem,"image"):
            imageUrl = rssItem["image"].get("href","")

        podcastEpisode = PodcastEpisode(podcastName, episode_title, show_notes_link, download_url, publishedDate, duration, author, summary, additionalLinks, imageUrl)
        return podcastEpisode
    
    def write_seen_cache(self, cache_folder_path):
        if(self.parsed_feed==None):
            return
        
        cache_file_name = self.__cached_file_name()
        filepath = path.join(cache_folder_path,cache_file_name)

        with open(filepath, 'w', newline='') as csvfile:
            print("\nWriting seen cache for ", cache_file_name)
            rss_list_writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            for item in self.seen_podcast_episodes:
                rss_list_writer.writerow([item.podcastName, item.title, item.show_notes_url, item.download_url])