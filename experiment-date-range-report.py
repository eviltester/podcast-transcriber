# this would be easier with a db, but currently file based so scan meta data
import os
import yaml
from dateutil.parser import parse
from unicodedata import normalize

from podcast_episode import load_the_podcast_episode_data, load_the_podcast_episode_data_from_file


class PodcastInfo:
    def __init__(self, name, episode, released, directory):
        self.podcastname = name
        self.episodename = episode
        self.releaseDate = released
        self.directory = directory

podcasts = []

def getPodcastMetaData(rootdir):
    # load all metadata
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file

            if filepath.endswith("episode.json"):
                episode = load_the_podcast_episode_data_from_file(filepath)
                podcastName = episode.podcastName
                episodename = episode.title
                published = episode.published
                podcastInfo = PodcastInfo(podcastName, episodename, published, os.path.dirname(filepath))
                print(".", end='')
                podcasts.append(podcastInfo)

podcastDataFolder = "d:/git/dev/python/podcast-transcriptions"
getPodcastMetaData(podcastDataFolder)

outputFolderName = "output-reports/2025-06-june"
fromDate = parse("2025-06-01 00:00:01 UTC")
toDate = parse("2025-06-30 23:59:59 UTC")

#dateRangedPodcasts = []


# filter podcasts to the date range
dateRangedPodcasts = list(filter(lambda p: (fromDate <= p.releaseDate <= toDate), podcasts))

# for podcast in podcasts:
#     if fromDate <= podcast.releaseDate <= toDate:
#         dateRangedPodcasts.append(podcast)
#         print(yaml.dump(podcast, indent=2))

# sort in date order
dateRangedPodcasts.sort(key=lambda p: p.releaseDate)

outputPath = os.path.join(podcastDataFolder, outputFolderName)
if not os.path.exists(outputPath):
    os.makedirs(outputPath)

for podcast in dateRangedPodcasts:
    print(yaml.dump(podcast, indent=2))

# create a summary list

with open(os.path.join(outputPath,"summary-list.md"),"w") as f:
    for podcast in dateRangedPodcasts:
        print(yaml.dump(podcast, indent=2))
        f.write(f"\n\n- {podcast.podcastname}]\n")
        f.write(f"\n\n- {podcast.releaseDate}]\n\n\n")
        # output links etc. here

# create a combined markdown + feed into pandoc
# summary-title.md
# summary.md
newpagebreak = "\\newpage"
addPageBreak = True

#todo: create reports based on categories e.g. testing, ai, etc. (this needs to be defined at a podcast feed meta-data level on podcastname)

with open(os.path.join(outputPath,"summary-details.md"),"w") as f:
    for podcast in dateRangedPodcasts:
        includeEpisode = True
        if podcast.podcastname == "MLOps.community":
            includeEpisode = False

        if includeEpisode:
            if addPageBreak:
                f.write(newpagebreak)
            addPageBreak=True
            inputPath = podcast.directory
            nameAsDir = os.path.basename(inputPath)
            print(yaml.dump(podcast, indent=2))
            # todo: if we have not created a transcript then create it now
            # todo: if main summary does not exist then create it now
            # todo: really need to normalize earlier for all text
            with open(os.path.join(inputPath,f"summary-{nameAsDir}.md"),"r", errors="ignore") as summary:
                summarymd = summary.read()
            summarymd = normalize('NFD', summarymd).encode('ascii','ignore').decode('utf-8')
            f.write(f"\n\n{summarymd}\n\n---\n\n")

# todo: call pandocifier to generate pdf
# pandoc summary-details.md -f markdown -s -o summary-report.pdf --toc --toc-depth=4