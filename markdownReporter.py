import json
import os.path

from downloads import filenameify


# for a given file
# extract the folder

def generateMarkdownSummaryReport(aTranscriptFile):
    outputPath = os.path.dirname(aTranscriptFile)
    metadataFilePath = os.path.join(outputPath, "metadata.json")
    if not os.path.exists(metadataFilePath):
        print(f"cannot generate report as metadata.json does not exist for {outputPath}")
        exit()
    summaryFilePath = os.path.join(outputPath, "summary.md")
    if not os.path.exists(metadataFilePath):
        # TODO: for backwards compatibility could look for aTranscriptFile.notes.md and copy to summary.md in folder then continue
        print(f"cannot generate report as summary.md does not exist for {outputPath}")
        exit()

    with open(metadataFilePath) as f:
        metaData = json.load(f)


    title = metaData.get("title","")
    titleAsFile = filenameify(title)
    summaryReportFileName = os.path.join(outputPath,f"summary-{titleAsFile}.md")


    author = metaData.get("author","")

    showNotes = metaData.get("link","")
    links = metaData.get("links",[])
    podcastName = metaData.get("podcastname","")
    published = metaData.get("published","")
    duration = metaData.get("itunes_duration","")
    episodeLink = ""
    if metaData.get("title_detail", "") != "":
        if metaData["title_detail"].get("base","") != "":
            episodeLink = metaData["title_detail"]["base"]

    summary = ""
    with open(summaryFilePath,"r") as file:
        summary = file.read()

    with open(summaryReportFileName, 'w') as f:
        f.write(f"# {podcastName} - Episode Summary - {title}\n\n")
        f.write(f"\n**Episode Details**\n\n")
        if podcastName != "":
            f.write(f"- {podcastName}\n")
        if title != "":
            f.write(f"- {title}\n")
        if duration != "":
            f.write(f"- {duration}\n")
        if published != "":
            f.write(f"- {published}\n")
        if author != "":
            f.write(f"- {author}\n")
        if showNotes != "":
            f.write(f"- [Show Notes]({showNotes})\n")
        for link in links:
            rel = link.get("rel","")
            type = link.get("type","")
            href = link.get("href","")
            f.write(f"- [{rel} - {type}]({href})\n")
        if episodeLink != "":
            f.write(f"- [Episode Link]({episodeLink})")
        f.write(f"\n\n{summary}\n\n")
