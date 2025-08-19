from downloads import filenameify
import os
import json

from podcastrss.RssFeed import RssFeed


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

    def save_feeds_to_json(self, filepath):
        """Save a list of RssFeed objects to a single JSON file."""
        try:
            feeds_data = [feed.to_dict() for feed in self.feeds]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(feeds_data, f, indent=2, ensure_ascii=False)
            print(f"{len(self.feeds)} RssFeeds saved to {filepath}")
        except Exception as e:
            print(f"Error saving feeds to JSON: {e}")

    def load_feeds_from_json(self, filepath):
        """Load a list of RssFeed objects from a single JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                feeds_data = json.load(f)

            self.feeds = []
            for feed_data in feeds_data:
                feed = RssFeed.from_dict(feed_data)
                self.feeds.append(feed)

            print(f"{len(self.feeds)} RssFeeds loaded from {filepath}")
            return self.feeds

        except FileNotFoundError:
            print(f"File {filepath} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return []
        except Exception as e:
            print(f"Error loading feeds from JSON: {e}")
            return []