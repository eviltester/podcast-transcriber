import csv
import feedparser
from os import path, makedirs
from unicodedata import normalize
import json
from dateutil.parser import parse

from downloads import filenameify

class RssCachedShow:
    def __init__(self, feedname, title, show_notes_url, download_url, published=None):
        self.feedname =  normalize('NFD', feedname).encode('ascii','ignore').decode('utf-8')
        self.title =  normalize('NFD', title).encode('ascii','ignore').decode('utf-8')
        self.show_notes_url = show_notes_url
        self.download_url = download_url
        if published is None:
            self.published = published
        else:
            if isinstance(published, str):
                self.published = parse(published)
            else:
                self.published = published


class RssListReader:
    # CSV file with
    # feed name, feedurl
    def __init__(self, filepath):
        self.filepath = filepath
        self.feeds = []

    def loadFeeds(self):
        with open(self.filepath, newline='') as csvfile:
            rss_list_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in rss_list_reader:
                self.feeds.append(RssFeed(feedname = row[0], feed_rss_url=row[1]))

# this is a complete hack - we should have proper serialization at a minimum, but really a DB
def store_the_episode_rss_meta_data(outputFolder, podcastname, item):
    cachedData = RssCachedShow(podcastname, item.title, "", "")
    # hack - create the podcast folder - normally done during transcription
    outputFileFolder = path.join(outputFolder, filenameify(cachedData.feedname), filenameify(cachedData.title))
    if not path.exists(outputFileFolder):
        makedirs(outputFileFolder)
    metaDataFile = path.join(outputFileFolder, "metadata.json")
    if not path.exists(metaDataFile):
        aDict = json.loads(json.dumps(item))
        # now add other metadata
        aDict["podcastname"] = podcastname
        with open(metaDataFile, 'w') as f:
            json.dump(aDict, f, sort_keys = True, indent=4)


class RssFeed:
    def __init__(self, feedname, feed_rss_url, categories=None, homeUrl="", hrefs=None, earliestAutoDownloadDate=None):
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

        self.new_items = []
        self.seen_items = []
        self.seen_urls = set()
        self.new_urls = set()
        self.cache_path = ""

    def add_to_seen_cache(self, anItem):
        if(anItem.download_url in self.seen_urls):
            print("Removing duplicate from seen cache", anItem.download_url)
        else:
            self.seen_urls.add(anItem.download_url)
            self.seen_items.append(anItem)


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
                    self.seen_items.append(RssCachedShow(feedname = row[0], title=row[1], show_notes_url=row[2], download_url=row[3]))

    def find_new_rss_items(self):

        if(self.parsed_feed==None):
            print("feed not loaded")

        # base newness on "have I seen this download url" before?
        for item in self.parsed_feed.entries:
            download_url=""

            store_the_episode_rss_meta_data(self.cache_path, self.feedname, item)

            for aLink in item.links:
                if(aLink.type=="audio/mpeg" or aLink.type=="audio/x-m4a" or aLink.type.startswith("audio/")):
                    download_url = aLink.href
            if(download_url==""):
                print("error parsing rss feed cannot find download url for item " + item.title + " - " + item.link)
                # try to find in enclosure
                for anEnclosure in item.enclosures:
                    if(anEnclosure.type=="audio/mpeg" or anEnclosure.type=="audio/x-m4a" or anEnclosure.type.startswith("audio/")):
                        if(hasattr(anEnclosure, "href")):
                            download_url = anEnclosure.href
                        if(download_url=="" and hasattr(anEnclosure, "url")):
                            download_url = anEnclosure.url
            
            seen_before = False
            for seen in self.seen_items:
                if(seen.download_url == download_url):
                    print("seen episode before " + item.title)
                    seen_before = True
                    break

            show_notes_link = ""
            if(hasattr(item, "link")):
                show_notes_link = item.link

            publishedDate = parse(item.get("published",None))

            if(not seen_before):
                if(download_url in self.new_urls):
                    print("not adding duplicate new item ", item.title)
                else:
                    self.new_urls.add(download_url)
                    self.new_items.append(RssCachedShow(self.feedname, item.title, show_notes_link, download_url, publishedDate))
    
    def write_seen_cache(self, cache_folder_path):
        if(self.parsed_feed==None):
            return
        
        cache_file_name = self.__cached_file_name()
        filepath = path.join(cache_folder_path,cache_file_name)

        with open(filepath, 'w', newline='') as csvfile:
            print("Writing seen cache for ", cache_file_name)
            rss_list_writer = csv.writer(csvfile, delimiter=',', quotechar='"')
            for item in self.seen_items:
                rss_list_writer.writerow([item.feedname, item.title, item.show_notes_url, item.download_url])