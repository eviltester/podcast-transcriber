# this would be easier with a db, but currently file based so scan meta data
from dateutil.parser import parse

from reports.pandoc_report_generator import PandocReportGenerator

# class PodcastInfo:
#     def __init__(self, name, episode, released, directory):
#         self.podcastname = name
#         self.episodename = episode
#         self.releaseDate = released
#         self.directory = directory
#
#
#
# def getPodcastMetaData(rootdir):
#     # load all metadata
#     for subdir, dirs, files in os.walk(rootdir):
#         for file in files:
#             #print os.path.join(subdir, file)
#             filepath = subdir + os.sep + file
#
#             if filepath.endswith("episode.json"):
#                 episode = load_the_podcast_episode_data_from_file(filepath)
#                 podcastName = episode.podcastName
#                 episodename = episode.title
#                 published = episode.published
#                 podcastInfo = PodcastInfo(podcastName, episodename, published, os.path.dirname(filepath))
#                 print(".", end='')
#                 podcasts.append(podcastInfo)
#
#
# def output_podcast_summary_list(type_name, output_path, podcasts_to_output, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
#     with open(os.path.join(output_path,f"summary-list-{type_name}.md"),"w") as f:
#         for podcast in podcasts_to_output:
#
#             include_episode = should_include_podcast_named(podcast.podcastname, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
#
#             if include_episode:
#                 print(yaml.dump(podcast, indent=2))
#                 f.write(f"\n\n- {podcast.podcastname}]\n")
#                 f.write(f"\n\n- {podcast.releaseDate}]\n\n\n")
#                 # output links etc. here
#
#
# def find_podcast_definition(podcast_name, podcast_definitions):
#     if podcast_definitions is None:
#         return None
#
#     for aPodcastDefinition in podcast_definitions:
#         if aPodcastDefinition.feedname == podcast_name:
#             return aPodcastDefinition
#
#     return None
#
# def should_include_podcast_named(podcast_name, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
#     includeEpisode = True
#     if podcast_name in exclude_podcast_names:
#         includeEpisode = False
#
#     if includeEpisode and podcast_definitions is not None:
#         if podcast_categories_to_include is not None:
#             podcast_definition = find_podcast_definition(podcast_name, podcast_definitions)
#             if podcast_definition is not None:
#                 category_include = False
#                 for aCategory in podcast_definition.categories:
#                     if podcast_categories_to_include.indexOf(aCategory) > -1:
#                         category_include = True
#                 includeEpisode = category_include
#
#     return includeEpisode
#
#
#
# def create_summary_report(type_name, output_path, podcasts_to_output, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
#
#     base_file_name = f"summary-details-{type_name}"
#     md_filename = f"{base_file_name}.md"
#
#     # create a combined markdown + feed into pandoc
#     # summary-title.md
#     # summary.md
#     newpagebreak = "\\newpage"
#     addPageBreak = True
#
#     with open(os.path.join(output_path,md_filename),"w") as f:
#         for podcast in podcasts_to_output:
#             includeEpisode = should_include_podcast_named(podcast.podcastname, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
#             # if podcast.podcastname in exclude_podcast_names:
#             #     includeEpisode = False
#             #
#             # if includeEpisode and podcast_definitions is not None:
#             #     if podcast_categories_to_include is not None:
#             #         podcast_definition = find_podcast_definition(podcast.podcastname, podcast_definitions)
#             #         if podcast_definition is not None:
#             #             category_include = False
#             #             for aCategory in podcast_definition.categories:
#             #                 if podcast_categories_to_include.indexOf(aCategory) > -1:
#             #                     category_include = True
#             #             includeEpisode = category_include
#
#             if includeEpisode:
#                 if addPageBreak:
#                     f.write(newpagebreak)
#                 addPageBreak=True
#                 inputPath = podcast.directory
#                 nameAsDir = os.path.basename(inputPath)
#                 print(yaml.dump(podcast, indent=2))
#                 # todo: if we have not created a transcript then create it now
#                 # todo: if main summary does not exist then create it now
#                 # todo: really need to normalize earlier for all text
#                 with open(os.path.join(inputPath,f"summary-{nameAsDir}.md"),"r", errors="ignore") as summary:
#                     summarymd = summary.read()
#                 summarymd = normalize('NFD', summarymd).encode('ascii','ignore').decode('utf-8')
#
#                 # we had issues where AI generated summary might have "---" or "--- " without 2 newline break
#                 # which caused pandoc to treat it as yaml markdown
#                 summarymd = re.sub(r"^---[ ]*\n([^\n])",r"---\n\n\1", summarymd, flags=re.M)
#
#                 f.write(f"\n\n{summarymd}\n\n---\n\n")
#
#     # call pandocifier to generate pdf
#     # pandoc summary-details.md -f markdown -s -o summary-report.pdf --toc --toc-depth=4
#     subprocess.run(["pandoc",os.path.join(output_path,md_filename), "-f","markdown", "-s", "-o", os.path.join(output_path,f"{base_file_name}-report.pdf"),"--toc", "--toc-depth=4"])
#
#
#
# def generate_reports_for(fromDate, toDate, podcasts, type_name,  outputPath, exclude_podcast_names, podcast_categories_to_include, podcast_definitions):
#
#     #dateRangedPodcasts = []
#
#     # filter podcasts to the date range
#     dateRangedPodcasts = list(filter(lambda p: (fromDate <= p.releaseDate <= toDate), podcasts))
#
#     # for podcast in podcasts:
#     #     if fromDate <= podcast.releaseDate <= toDate:
#     #         dateRangedPodcasts.append(podcast)
#     #         print(yaml.dump(podcast, indent=2))
#
#     # sort in date order
#     dateRangedPodcasts.sort(key=lambda p: p.releaseDate)
#
#     for podcast in dateRangedPodcasts:
#         print(yaml.dump(podcast, indent=2))
#
#     output_podcast_summary_list(type_name, outputPath, dateRangedPodcasts, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
#     create_summary_report(type_name, outputPath, dateRangedPodcasts, exclude_podcast_names, podcast_categories_to_include, podcast_definitions)
#
#
#
# podcasts = []
#
# podcastDataFolder = "d:/git/dev/python/podcast-transcriptions"
# getPodcastMetaData(podcastDataFolder)
#
# outputFolderName = "output-reports/2025-07-july"
#
# outputPath = os.path.join(podcastDataFolder, outputFolderName)
# if not os.path.exists(outputPath):
#     os.makedirs(outputPath)
#
# fromDate = parse("2025-07-01 00:00:01 UTC")
# toDate = parse("2025-07-31 23:59:59 UTC")
#
# # create a summary list
# #todo: create reports based on categories e.g. testing, ai, etc. (this needs to be defined at a podcast feed meta-data level on podcastname)
# podcast_names_to_exclude = ["MLOps.community","Technovation", "Fastlane Founders"]
#
# generate_reports_for(fromDate, toDate, podcasts, "testing", outputPath, podcast_names_to_exclude, [], [])

# output_podcast_summary_list("testing", outputPath, dateRangedPodcasts, podcast_names_to_exclude, [], [])
# create_summary_report("testing", outputPath, dateRangedPodcasts, podcast_names_to_exclude, [], [])

podcastDataFolder = "d:/git/dev/python/podcast-transcriptions"
outputFolderName = "output-reports/2025-07-july"
fromDate = parse("2025-07-01 00:00:01 UTC")
toDate = parse("2025-07-31 23:59:59 UTC")
#todo: create reports based on categories e.g. testing, ai, etc. (this needs to be defined at a podcast feed meta-data level on podcastname)
podcast_names_to_exclude = ["MLOps.community","Technovation", "Fastlane Founders"]

reporter = PandocReportGenerator(podcastDataFolder, outputFolderName)
reporter.generate_reports_for(fromDate, toDate, "testing", podcast_names_to_exclude, [], [])