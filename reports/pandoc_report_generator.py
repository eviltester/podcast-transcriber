import os
import yaml
from unicodedata import normalize
import subprocess
import re

from podcast_episode import load_the_podcast_episode_data, load_the_podcast_episode_data_from_file

class PodcastInfo:
    def __init__(self, name, episode, released, directory):
        self.podcastname = name
        self.episodename = episode
        self.releaseDate = released
        self.directory = directory

class PandocReportGenerator:

    def __init__(self, podcast_data_folder, output_folder_name):
        self.podcasts =  []
        self.podcast_data_root_folder = podcast_data_folder

        self.getPodcastMetaData(self.podcast_data_root_folder)

        self.outputPath = os.path.join(podcast_data_folder, output_folder_name)
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)



    def getPodcastMetaData(self, rootdir):
        # load all metadata
        # TODO: create a dot_line_progress_printer that maintains its own dot_count
        dot_count = 0
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
                    if dot_count % 25 == 0:
                        print(".")
                    else:
                        print(".", end='')
                    dot_count += 1
                    self.podcasts.append(podcastInfo)


    def output_podcast_summary_list(self, type_name, output_path, podcasts_to_output, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
        with open(os.path.join(output_path,f"summary-list-{type_name}.md"),"w") as f:
            for podcast in podcasts_to_output:

                include_episode = self.should_include_podcast_named(podcast.podcastname, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)

                if include_episode:
                    print(yaml.dump(podcast, indent=2))
                    f.write(f"\n\n- {podcast.podcastname}]\n")
                    f.write(f"\n\n- {podcast.releaseDate}]\n\n\n")
                    # output links etc. here


    def find_podcast_definition(self, podcast_name, podcast_definitions):
        if podcast_definitions is None:
            return None

        for aPodcastDefinition in podcast_definitions:
            if aPodcastDefinition.feedname == podcast_name:
                return aPodcastDefinition

        return None

    def should_include_podcast_named(self, podcast_name, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
        includeEpisode = True
        if podcast_name in exclude_podcast_names:
            includeEpisode = False

        if includeEpisode and podcast_definitions is not None:
            if podcast_categories_to_include is not None:
                podcast_definition = self.find_podcast_definition(podcast_name, podcast_definitions)
                if podcast_definition is not None:
                    category_include = False
                    for aCategory in podcast_definition.categories:
                        if aCategory in podcast_categories_to_include:
                            category_include = True
                    includeEpisode = category_include

        return includeEpisode



    def create_summary_report(self, type_name, output_path, podcasts_to_output, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):

        base_file_name = f"summary-details-{type_name}"
        md_filename = f"{base_file_name}.md"

        # create a combined markdown + feed into pandoc
        # summary-title.md
        # summary.md
        newpagebreak = "\\newpage"
        addPageBreak = True

        with open(os.path.join(output_path,md_filename),"w") as f:
            for podcast in podcasts_to_output:
                includeEpisode = self.should_include_podcast_named(podcast.podcastname, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
                # if podcast.podcastname in exclude_podcast_names:
                #     includeEpisode = False
                #
                # if includeEpisode and podcast_definitions is not None:
                #     if podcast_categories_to_include is not None:
                #         podcast_definition = find_podcast_definition(podcast.podcastname, podcast_definitions)
                #         if podcast_definition is not None:
                #             category_include = False
                #             for aCategory in podcast_definition.categories:
                #                 if podcast_categories_to_include.indexOf(aCategory) > -1:
                #                     category_include = True
                #             includeEpisode = category_include

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

                    # we had issues where AI generated summary might have "---" or "--- " without 2 newline break
                    # which caused pandoc to treat it as yaml markdown
                    summarymd = re.sub(r"^---[ ]*\n([^\n])",r"---\n\n\1", summarymd, flags=re.M)

                    f.write(f"\n\n{summarymd}\n\n---\n\n")

        # call pandocifier to generate pdf
        # pandoc summary-details.md -f markdown -s -o summary-report.pdf --toc --toc-depth=4
        subprocess.run(["pandoc",os.path.join(output_path,md_filename), "-f","markdown", "-s", "-o", os.path.join(output_path,f"{base_file_name}-report.pdf"),"--toc", "--toc-depth=4"])


    def generate_reports_for(self, fromDate, toDate, type_name, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):

        #dateRangedPodcasts = []

        # filter podcasts to the date range
        dateRangedPodcasts = list(filter(lambda p: (fromDate <= p.releaseDate <= toDate), self.podcasts))

        # for podcast in podcasts:
        #     if fromDate <= podcast.releaseDate <= toDate:
        #         dateRangedPodcasts.append(podcast)
        #         print(yaml.dump(podcast, indent=2))

        # sort in date order
        dateRangedPodcasts.sort(key=lambda p: p.releaseDate)

        for podcast in dateRangedPodcasts:
            print(yaml.dump(podcast, indent=2))

        self.output_podcast_summary_list(type_name, self.outputPath, dateRangedPodcasts, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
        self.create_summary_report(type_name, self.outputPath, dateRangedPodcasts, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)