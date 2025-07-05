from ollama import generate
import sys
import os


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
    def __init__(self, modelname, title, prompt, response):
        self.modelname = modelname
        self.prompt = prompt
        self.title = title
        self.response = response


def generateFromModel(modelname, title, prompt):
    print(f"Executing prompt for {title} on {modelname}")
    text = generate(model=modelname, prompt=prompt)
    return Response(modelname, title, prompt, text.response)


print(f"Read File {fileToRead}")

print("Getting Ready for summarization")

#
# ---------
#

responses = []

# any models used should first have been pulled into ollama - `ollama pull llama3.1`

print("Starting to Summarize")

gemmaControlText = "\n\n Add --- before and after your response."

def generateFromPrompt(responsesArray, filecontents, title, prompt):
    gemmaControlText = "\n\n Add --- before and after your response."
    # https://ollama.com/library/llama3.1
    #responsesArray.append(generateFromModel("llama3.1", title + " LLAMA 3.1", f"{prompt} {filecontents}"))
    # https://ollama.com/library/dolphin3
    # creates bullets like mistral but doesn't hallucinate as much - might be best
    responsesArray.append(generateFromModel("dolphin3", title + " DOLPHIN3", f"{prompt} {filecontents}"))
    # https://ollama.com/library/magistral
    # magistral is good but slow
    # responsesArray.append(generateFromModel("magistral", title + " MAGISTRAL", f"{prompt} {filecontents}"))
    # https://ollama.com/library/mistral
    # Mistral likes to hallucinate names but creates bullet lists well
    #responsesArray.append(generateFromModel("mistral", title + " MISTRAL", f"{prompt} {filecontents}"))
    #https://ollama.com/library/gemma3
    # gemma3 is too chatty and likes to critique rather than do what it is told
    #responsesArray.append(generateFromModel("gemma3", title + " GEMMA3", f"{prompt} {filecontents} {gemmaControlText}"))

generalSummaryPrompt = "Summarize the main topics discussed in the following text. Use bullets and headings. Here is the text to summarize:\n\n"
generateFromPrompt(responses, filecontents, "Main Topics", generalSummaryPrompt)


# https://veritysangan.com/chatgpt-podcast-show-notes-prompts/

chattysummary = "Can you summarise the main topics discussed in the podcast episode, and provide a brief overview of how they were explored or analysed? I need approximately 300 words for podcast show notes and I need the show notes to be written in an informal and chatty manner using the following transcription\n\n"
generateFromPrompt(responses, filecontents, "Chatty Summary", chattysummary)

keyinsightsprompt = "Use the following podcast transcript and identify some of the key insights or takeaways presented in the podcast episode, and how might they be relevant or useful to listeners. I need you to use this information to create podcast show notes. Here is the transcript "
generateFromPrompt(responses, filecontents, "Key Insights", keyinsightsprompt)


notablequotes = "Can you identify any notable quotes, anecdotes, or examples from the podcast episode that help illustrate the main points or themes discussed to create show notes for this podcast episodes. Use this transcript to write the show notes\n\n"
generateFromPrompt(responses, filecontents, "Notable Quotes", notablequotes)

actionprompt = "Create a list of action items from the following text: \n\n"
generateFromPrompt(responses, filecontents, "Actionable items", actionprompt)

briefOverview = "Based on the transcript of this podcast episode, can you provide a brief introduction or overview that effectively captures the main theme or takeaway of the episode. I need the show notes to be around 200 words long and written in a persuasive way to engage the reader. Here is the transcript \n\n"
generateFromPrompt(responses, filecontents, "Breif Overview", briefOverview)

for response in responses:
    print(f"\n\n# {response.title}")
    print("\n\n" + response.response)


