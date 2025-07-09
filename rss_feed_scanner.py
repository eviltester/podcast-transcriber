from downloads import DownloadFile
from dateutil.parser import parse

class RssFeedScanner:

    def __init__(self, outputPath, download_queue, rssList, download_path):
        self.outputPath =  outputPath
        self.download_queue = download_queue
        self.rssList = rssList
        self.download_path = download_path

    def scan_for_new_podcasts(self):
        for rss_feed in self.rssList.feeds:

            rss_feed.load()

            rss_feed.load_seen_cache(self.outputPath)
            rss_feed.find_new_rss_items()

            for item in rss_feed.new_podcast_episodes:
                print (item.title + " - " + item.download_url)

                # add new items to download queue
                # by default download everything
                should_download = True
                if rss_feed.earliestAutoDownloadDate != None:
                    earliestdownload = parse(rss_feed.earliestAutoDownloadDate)
                    itempublished = None
                    if not item.published is None:
                        itempublished  = item.published
                    if not itempublished is None and itempublished < earliestdownload:
                        should_download = False

                # todo: check if already downloaded and processed
                if should_download:
                    self.download_queue.add(DownloadFile(item.podcastName, item.title, self.download_path, item.download_url))
                rss_feed.add_to_seen_cache(item)

            # write rss cache file
            self.download_queue.save_caches()
            rss_feed.write_seen_cache(self.outputPath)