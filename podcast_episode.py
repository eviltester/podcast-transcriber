# PodcastEpisode is a class that encompasses all the meta data for a podcast episode
# mostly taken from the RSS feed in rss.py
from unicodedata import normalize
from dateutil.parser import parse
import json
from downloads import filenameify
from os import path, makedirs

class PodcastEpisode:
    def __init__(self, podcast_name, title, show_notes_url, download_url, published, duration, author, summary, links, image_url):
        self.podcastName =  normalize('NFD', podcast_name)
        self.title =  normalize('NFD', title).encode('ascii','ignore').decode('utf-8')
        self.show_notes_url = show_notes_url
        self.download_url = download_url

        # date episode was published
        # if passed in as a string then try to parse it
        # todo: if not created with a timezone then there will be problems later, enforce this
        if isinstance(published, str):
            self.published = parse(published)
        else:
            self.published = published

        self.duration = duration
        self.author = normalize('NFD', author).encode('ascii','ignore').decode('utf-8')
        self.summary = normalize('NFD', summary).encode('ascii','ignore').decode('utf-8')

        # links should be a dict of [name](url)
        self.links = links

        self.imageUrl = image_url

    def asDict(self):

        output = {}
        output.update({"podcastname" : self.podcastName,
                       "title" : self.title,
                       "show_notes_url" : self.show_notes_url,
                       "download_url" : self.download_url,
                       "published" : self.published.strftime('%Y-%m-%d %H:%M:%S UTC'),
                       "duration" : self.duration,
                       "author" : self.author,
                       "links" : self.links,
                       "summary" : self.summary,
                       "imageurl" : self.imageUrl
                       })
        return output

    @staticmethod
    def fromDict(aDict):
        podcastName = aDict.get("podcastname")
        title = aDict.get("title")
        show_notes_url = aDict.get("show_notes_url")
        download_url = aDict.get("download_url")
        published = aDict.get("published")
        duration = aDict.get("duration")
        author = aDict.get("author")
        links =  aDict.get("links")
        summary = aDict.get("summary")
        imageurl  = aDict.get("imageurl")

        return PodcastEpisode(podcastName, title, show_notes_url, download_url, published, duration, author, summary, links, imageurl)



# this is a complete hack - we should have proper serialization at a minimum, but really a DB
# todo this should probably be a 'repository' that we pass into the find_new_items method and save the date through that
def store_the_podcast_episode_data(outputFolder, episode):
    outputFileFolder = path.join(outputFolder, filenameify(episode.podcastName), filenameify(episode.title))
    if not path.exists(outputFileFolder):
        makedirs(outputFileFolder)
    episodeDataFile = path.join(outputFileFolder, "episode.json")
    if not path.exists(episodeDataFile):
        # output = json.dumps(episode.asDict())
        # togetback = PodcastEpisode.fromDict(json.loads(output))
        with open(episodeDataFile, 'w') as f:
            json.dump(episode.asDict(), f, sort_keys = True, indent=4)

def load_the_podcast_episode_data(basefolder, podcastname, episodetitle):
    inputFileFolder = path.join(basefolder, filenameify(podcastname), filenameify(episodetitle))
    episodeDataFile = path.join(inputFileFolder, "episode.json")
    return load_the_podcast_episode_data_from_file(episodeDataFile)

def load_the_podcast_episode_data_from_file(aFilePath):
    if not path.exists(aFilePath):
        print("could not find episode data to load " + aFilePath)
        exit()
    else:
        with open(aFilePath, 'r') as f:
            return PodcastEpisode.fromDict(json.load(f))