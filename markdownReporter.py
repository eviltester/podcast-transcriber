import os.path

from downloads import filenameify
from podcast_episode import load_the_podcast_episode_data

# for a given file
# extract the folder

def generateMarkdownSummaryReport(outputPath, podcastName, episodeTitle):

    # title = metaData.get("title","")
    podcastNameAsFile = filenameify(podcastName)
    titleAsFile = filenameify(episodeTitle)

    summaryFilePath = os.path.join(outputPath, podcastNameAsFile, titleAsFile, "summary.md")
    if not os.path.exists(summaryFilePath):
        # TODO: for backwards compatibility could look for aTranscriptFile.notes.md and copy to summary.md in folder then continue
        print(f"cannot generate report as summary.md does not exist for {outputPath}")
        exit()

    summaryReportFileName = os.path.join(outputPath,podcastNameAsFile, titleAsFile,f"summary-{titleAsFile}.md")

    episode = load_the_podcast_episode_data(outputPath, podcastName, episodeTitle)

    summary = ""
    with open(summaryFilePath,"r") as file:
        summary = file.read()

    with open(summaryReportFileName, 'w') as f:
        f.write(f"# {episode.podcastName} - Episode Summary - {episode.title}\n\n")
        f.write(f"\n**Episode Details**\n\n")
        if episode.podcastName != "":
            f.write(f"- Podcast: {episode.podcastName}\n")
        if episode.title != "":
            f.write(f"- Title: {episode.title}\n")
        if episode.duration != "":
            f.write(f"- Duration: {episode.duration}\n")
        if episode.published != "":
            f.write(f"- Published: {episode.published}\n")
        if episode.author != "":
            f.write(f"- Author: {episode.author}\n")
        if episode.show_notes_url != "":
            f.write(f"- [Show Notes]({episode.show_notes_url})\n")
        if episode.download_url != "":
            f.write(f"- [Download]({episode.download_url})\n")
        for link in episode.links:
            f.write(f"- [{link}]({episode.links[link]})\n")
        if episode.summary != "":
            f.write(f"\n\n---\n\n{episode.summary}\n\n---\n\n")
        f.write(f"\n\n{summary}\n\n")
