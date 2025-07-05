from ollama import generate
import sys
import os
from unicodedata import normalize


def readFileContents(fileToRead):
    print(f"Read File {fileToRead}")

    if not os.path.isfile(fileToRead):
        print("File does not exist: " + fileToRead)
        exit()

    print("Reading File:" + fileToRead)
    with open(fileToRead,"r") as file:
        filecontents = file.read()
    return filecontents


class Response:
    def __init__(self, modelname, title, prompt, response):
        self.modelname = modelname
        self.prompt = prompt
        self.title = normalize('NFD', title).encode('ascii','ignore').decode('utf-8')
        self.response = normalize('NFD', response).encode('ascii','ignore').decode('utf-8')


def generateFromModel(modelname, title, prompt):
    print(f"Executing prompt for {title} on {modelname}")
    text = generate(model=modelname, prompt=prompt)
    return Response(modelname, title, prompt, text.response)




# any models used should first have been pulled into ollama - `ollama pull llama3.1`

def generateFromPrompt(responsesArray, filecontents, title, prompt, modelname = "dolphin3"):
    # https://ollama.com/library/dolphin3
    # creates bullets like mistral but doesn't hallucinate as much - might be best
    responsesArray.append(generateFromModel(modelname, title, f"{prompt} {filecontents}"))

def summarize(filecontents):

    print("Starting to Summarize")

    responses = []

    # need to tweak this
    generalSummaryPrompt = "Summarize the main topics discussed in the following text. Use bullets and headings. Here is the text to summarize:\n\n"
    generateFromPrompt(responses, filecontents, "Overview of Main Topics", generalSummaryPrompt, "mistral")

    # https://veritysangan.com/chatgpt-podcast-show-notes-prompts/

    briefOverview = "Based on the transcript of this podcast episode, can you provide a brief introduction or overview that effectively captures the main theme or takeaway of the episode. The show notes should be around 200 words long and written in a persuasive way to engage the reader. Here is the transcript \n\n"
    generateFromPrompt(responses, filecontents, "Brief Overview", briefOverview)

    chattysummary = "Summarise the main topics discussed in the podcast episode, and provide a brief overview of how they were explored or analysed? I need approximately 300 words for podcast show notes and I need the show notes to be written in a formal and direct manner using the following transcription\n\n"
    generateFromPrompt(responses, filecontents, "Summary", chattysummary)

    keyinsightsprompt = "Use the following text and identify some of the key insights or takeaways presented in the text, and how might they be relevant or useful to readers. Here is the text "
    generateFromPrompt(responses, filecontents, "Key Insights", keyinsightsprompt)

    actionprompt = "Create a list of action items that the reader can implement and take action on from the following text: \n\n"
    #generateFromPrompt(responses, filecontents, "Actionable Insights", actionprompt)

    notablequotes = "Can you identify any notable quotes, anecdotes, or examples from the text that help illustrate the main points or themes discussed to notes. Use this text to write the notes\n\n"
    #generateFromPrompt(responses, filecontents, "Final Notes", notablequotes)

    return responses


def printResponses(responses):
    for response in responses:
        print(f"\n\n## {response.title}")
        print("\n\n" + response.response)

def outputResponsesToFile(responses, fileToOutput):
    print("Writing Markdown Notes:" + fileToOutput)
    with open(fileToOutput,"w") as file:
        file.write(f"\n\n# Podcast Notes")
        # TODO: output the public meta data here as markdown
        for response in responses:
            file.write(f"\n\n## {response.title}")
            file.write("\n\n" + response.response + "\n\n")


def summarizeTranscriptFile(fileNameToRead):
    print("Getting Ready for summarization")
    filecontents = readFileContents(fileNameToRead)
    responses = summarize(filecontents)
    #printResponses(responses)
    fileToOutput = fileNameToRead + ".notes.md"
    outputResponsesToFile(responses, fileToOutput)
