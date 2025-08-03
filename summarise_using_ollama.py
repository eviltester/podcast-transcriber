from ollama import generate
import os
from unicodedata import normalize

from downloads import filenameify


def readFileContents(fileToRead):
    print(f"Read File {fileToRead}")

    if not os.path.isfile(fileToRead):
        print("File does not exist: " + fileToRead)
        exit()

    print("Reading File:" + fileToRead)
    with open(fileToRead,"r", errors="ignore") as file:
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
    # print(f"{title} - {text.response}")
    return Response(modelname, title, prompt, text.response)




# any models used should first have been pulled into ollama - `ollama pull llama3.1`

def generateFromPrompt(responsesArray, filecontents, title, prompt, modelname = "qwen3:8b"):
    # https://ollama.com/library/dolphin3
    # creates bullets like mistral but doesn't hallucinate as much - might be best
    prompt_to_use = prompt
    if modelname.startswith("qwen3"):
        prompt_to_use = "/no_think " + prompt

    response = generateFromModel(modelname, title, f"{prompt_to_use} {filecontents}")

    if modelname.startswith("qwen3"):
        response_to_edit = response.response
        start_thinking = response_to_edit.find("<think>")
        end_thinking = response_to_edit.find("</think>")
        if start_thinking != -1 and end_thinking != -1:
            response_to_edit = response_to_edit[0 : start_thinking] + response_to_edit[(end_thinking+len("</think>")) : len(response_to_edit)]
        response.response = response_to_edit

    responsesArray.append(response)


def chunk_filecontents(text_to_chunk, chunksize_chars, overrun_terminator):

    # split the given text into chunks of approximate chunksize_Chars
    # if the text hasn't ended by the final chunksize_chars length then carry on until we hit an overrun_terminator
    text_chunks = []
    current_char = 0
    current_chunk_start = 0
    looking_for_overrun_terminator = False
    current_chunk_size = 0
    text_length = len(text_to_chunk)
    max_chunk_size = chunksize_chars + 500

    while current_char < (text_length -1):
        current_char += 1
        current_chunk_size += 1

        if current_chunk_size > chunksize_chars:
            looking_for_overrun_terminator = True

        process_chunk = False

        if looking_for_overrun_terminator and text_to_chunk[current_char] == overrun_terminator:
            process_chunk = True

        #  override in case the paragraphs were too large - use sentence end
        if looking_for_overrun_terminator and current_chunk_size > max_chunk_size and text_to_chunk[current_char] == ".":
            print("chunk override at sentence end")
            process_chunk = True

        #  emregency override in case there is no punctuation - just stop at a word
        if looking_for_overrun_terminator and current_chunk_size > (max_chunk_size + 300) and text_to_chunk[current_char] == " ":
            print("emergency chunk override at word end")
            process_chunk = True

        if process_chunk:
            # we found a chunk
            print(f"chunking text ...{current_char-current_chunk_start}")
            text_chunks.append(text_to_chunk[current_chunk_start : current_char])

            # start looking for next chunk
            current_chunk_start = current_char + 1
            current_chunk_size = 0
            looking_for_overrun_terminator = False

    # deal with final chunk
    if current_chunk_start < text_length:
        print(f"final chunking text ...{(text_length-1) - current_chunk_start}")
        text_chunks.append(text_to_chunk[current_chunk_start : text_length-1])

    return text_chunks






def summarize(filecontents):

    print("Starting to Summarize")

    responses = []

    doc_sections = chunk_filecontents(filecontents, 6000, "\n")

    # "qwen3:14b"
    intermediate_response_model = "qwen3:14b"
    main_summary_model = "qwen3:14b"


    # for each doc_section, create a summary of it
    summary_responses = []
    intermediateSummaryPrompt = "Summarize the main topics discussed in the following text. Use bullets and headings. Here is the text to summarize:\n\n"
    for a_section in doc_sections:
        print("Summarizing chunk...")
        generateFromPrompt(summary_responses, a_section, "Intermediate", intermediateSummaryPrompt, intermediate_response_model)

    intermediate_text = ""
    for a_response in summary_responses:
        intermediate_text += a_response.response + "\n\n"

    # create single response for the intermediate responses
    responses.append(Response(intermediate_response_model, "Intermediate", intermediateSummaryPrompt, intermediate_text))

    # getting a paragraph was unreliable, just use the text provided in meta data
    #generalSummaryParaPrompt = "Summarize the main topics discussed in the following text as a short paragraph of writing:\n\n"
    #generateFromPrompt(responses, filecontents, "Main Summary", generalSummaryParaPrompt, "mistral")

    overviewSummaryPrompt = "Create a short 2 or 3 paragraph summary of the following text.\n\n"
    generateFromPrompt(responses, intermediate_text, "Overview", overviewSummaryPrompt, main_summary_model)

    briefingSummaryPrompt = "Create a briefing document from this text. Emphasize the important key points, particularly points that have used numbers in them. Create some introductory paragraphs and Use bullets and headings. Here is the text to create briefing document from:\n\n"
    generateFromPrompt(responses, intermediate_text, "Briefing", briefingSummaryPrompt, main_summary_model)

    generalSummaryPrompt = "Summarize the main topics discussed in the following text. Use bullets and headings. Here is the text to summarize:\n\n"
    generateFromPrompt(responses, intermediate_text, "Main Topics", generalSummaryPrompt, "qwen3:8b")


    keyinsightsprompt = "Use the following text and identify some of the key insights or takeaways presented in the text, and how might they be relevant or useful to readers. Here is the text "
    generateFromPrompt(responses, intermediate_text, "Final Notes", keyinsightsprompt, "llama3.1")

    return responses


def printResponses(responses):
    for response in responses:
        print(f"\n\n## {response.title}")
        print("\n\n" + response.response)

def outputResponsesToFile(responses, fileToOutput, titles_to_include, titles_to_exclude):
    print("Writing Markdown Notes:" + fileToOutput)
    with open(fileToOutput,"w") as file:
        # file.write(f"\n\n# Podcast Notes")
        # TODO: output the public meta data here as markdown
        for response in responses:

            # by default, output the response
            output_response = True
            if len(titles_to_include) > 0:
                if not response.title in titles_to_include:
                    output_response = False
            if len(titles_to_exclude) > 0:
                if response.title in titles_to_exclude:
                    output_response = False

            if output_response:
                file.write(f"\n\n## {response.title}")
                file.write("\n\n" + response.response + "\n\n")


def summarizeTranscriptFile(fileNameToRead):
    print("Getting Ready for summarization")
    filecontents = readFileContents(fileNameToRead)
    responses = summarize(filecontents)
    # printResponses(responses)
    outputPath = os.path.dirname(fileNameToRead)
    fileToOutput = fileNameToRead + ".notes.md"
    outputResponsesToFile(responses, fileToOutput, [], ["Intermediate","Main Topics"])
    outputResponsesToFile(responses, os.path.join(outputPath,"summary.md"), [], ["Intermediate","Main Topics"])
    for a_response in responses:
        outputResponsesToFile(responses, os.path.join(outputPath,filenameify(a_response.title.lower()) + "-summary.md"), [a_response.title], [])
