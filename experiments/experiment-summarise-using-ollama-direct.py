from ollama import generate
import sys
import os
import time


if len(sys.argv) == 1:
    #use hardcoded path, because I'm testing
    fileToRead = os.path.join(
        "D:/git/dev/python/podcast-transcriptions/the-eviltester-show/how-to-get-a-job-in-software-testing/how-to-get-a-job-in-software-testing-base.para.txt.md"
    )
else:
    fileToRead = sys.argv[1]

if not os.path.isfile(fileToRead):
    print("File does not exist: " + fileToRead)
    exit

print("Reading File:" + fileToRead)
with open(fileToRead,"r") as file:
    filecontents = file.read()


class Response:
    def __init__(self, modelname, title, prompt, response, seconds_to_generate):
        self.modelname = modelname
        self.prompt = prompt
        self.title = title
        self.response = response
        self.seconds_to_generate = seconds_to_generate


def generateFromModel(modelname, title, prompt):
    print(f"Executing prompt for {title} on {modelname}")
    start_time = time.time()
    text = generate(model=modelname, prompt=prompt)
    end_time = time.time()
    return Response(modelname, title, prompt, text.response, (end_time - start_time))


print(f"Read File {fileToRead}")

print("Getting Ready for summarization")

#
# ---------
#

responses = []

# any models used should first have been pulled into ollama - `ollama pull llama3.1`

print("Starting to Summarize")


#modelName = "magistral"
#modelPrefix = ""
#modelName = "gwen3:8b"
modelName = "gwen3:14b"
modelPrefix = "/no_think " # for gwen3 need to remove "<think>" and "</think>" from the output

generalSummaryParaPrompt = "Summarize the main topics discussed in the following text as a short paragraph of writing:\n\n"
responses.append(generateFromModel(modelName, "Main Summary", f"{modelPrefix} {generalSummaryParaPrompt} {filecontents}"))

generalSummaryPrompt = "Summarize the main topics discussed in the following text. Use bullets and headings. Here is the text to summarize:\n\n"
responses.append(generateFromModel(modelName, "Main Topics", f"{modelPrefix} {generalSummaryPrompt} {filecontents}"))

actionprompt = "Create a list of action items from the following text: \n\n"
responses.append(generateFromModel(modelName, "Actionable items", f"{actionprompt} {filecontents}"))

# https://veritysangan.com/chatgpt-podcast-show-notes-prompts/

# chattysummary = "Can you summarise the main topics discussed in the podcast episode, and provide a brief overview of how they were explored or analysed? I need approximately 300 words for podcast show notes and I need the show notes to be written in an informal and chatty manner using the following transcription\n\n"
# responses.append(generateFromModel(modelName, "Chatty Summary", f"{chattysummary} {filecontents}"))
#
# keyinsightsprompt = "Use the following podcast transcript and identify some of the key insights or takeaways presented in the podcast episode, and how might they be relevant or useful to listeners. I need you to use this information to create podcast show notes. Here is the transcript "
# responses.append(generateFromModel(modelName, "Key Insights", f"{keyinsightsprompt} {filecontents}"))
#
# notablequotes = "Can you identify any notable quotes, anecdotes, or examples from the podcast episode that help illustrate the main points or themes discussed to create show notes for this podcast episodes. Use this transcript to write the show notes\n\n"
# responses.append(generateFromModel(modelName, "Notable Quotes", f"{notablequotes} {filecontents}"))
#

#
# briefOverview = "Based on the transcript of this podcast episode, can you provide a brief introduction or overview that effectively captures the main theme or takeaway of the episode. I need the show notes to be around 200 words long and written in a persuasive way to engage the reader. Here is the transcript \n\n"
# responses.append(generateFromModel(modelName, "Brief Overview", f"{actionprompt} {filecontents}"))

for response in responses:
    print(f"# {modelName}")
    print(f"\n\n# {response.title} - {response.seconds_to_generate}")
    print("\n\n" + response.response)


