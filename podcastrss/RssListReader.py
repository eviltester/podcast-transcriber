import csv

from . import RssFeed


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