# quick test to see if we can summarize a transcript
import sys
import torch
import os
from transformers import pipeline

model_creator = "facebook"
model_name = "bart-large-cnn"

if len(sys.argv) == 1:
    #use hardcoded path, because I'm testing
    fileToRead = os.path.join("D:/git/dev/python/podcast-transcriptions/the-eviltester-show/how-to-get-a-job-in-software-testing/how-to-get-a-job-in-software-testing-base.para.txt.md"
                  )
else:
    fileToRead = sys.argv[1]

if not os.path.isfile(fileToRead):
    print("File does not exist: " + fileToRead)
    exit

print("Getting Ready for summarization")

if torch.cuda.is_available():
    print("Using CPU for summarization")
    summarizer = pipeline("summarization", model=f"{model_creator}/{model_name}", device=0)
else:
    print("Using GPU for summarization")
    summarizer = pipeline("summarization", model=f"{model_creator}/{model_name}")

# we may need to split the text, set a limit here
max_tokens_for_model = 1000

print("Ready to Summarize")


print("Reading " + fileToRead)
with open(fileToRead,"r") as file:
    filecontents = file.read()


print(f"Read File {fileToRead}")

# split large content into smaller chunks
# splitting text information
#  https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/split_by_token

chunk_size = 300
max_summary_size = chunk_size/2


# This works but is very crude as it splits sentences

# text_splitter = TokenTextSplitter(
#     chunk_size=chunk_size, chunk_overlap=0
# )

# texts = text_splitter.split_text(filecontents)





from langchain.text_splitter import CharacterTextSplitter

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=chunk_size, chunk_overlap=0
)
texts = text_splitter.split_text(filecontents)


# sometimes the splitter creates text that is too long for the summary model, so fix that here
textsToProcess = []
for text in texts:
    spacesInText = text.count(" ")
    if spacesInText>max_tokens_for_model:
        
        # split it
        words = text.split()
        print(f"having to split some text chunks... {len(words)}")
        start = 0
        while (start*max_tokens_for_model) < len(words):
            print("splitting...")
            startPos = (start*max_tokens_for_model)
            endPos=((start*max_tokens_for_model)+max_tokens_for_model)
            range = words[startPos:endPos]
            outputRangeSegment = " ".join(range)
            print(f"\nStartPos {startPos} : EndPos {endPos}\n\n{outputRangeSegment}")
            textsToProcess.append(outputRangeSegment)
            start = start+1
    else:
        textsToProcess.append(text)


texts = textsToProcess

# Summarize the chunks

print("Summarizing..." + str(len(texts)) + " sections")

summaryLines = []

for text in texts:
    print("Segment:\n\n" + text.replace("\r\n", " ").replace("\n", " ")  + "\n\n")

    minimumTokensToMakeSummarizationWorthDoing = 50
    # sometimes the text segment is smaller than we expect
    # so configure the max_length on the fly
    spacesInText = text.count(" ")
    print("\nEstimated token size " + str(spacesInText))
    
    summarySize = int(max_summary_size)


    if spacesInText<minimumTokensToMakeSummarizationWorthDoing:
        # text too small to summarize, just output it
        print(f"Summary:\n\n\n{text}\n\n")
        summaryLines.append(text)
    else:
        summarySize = int(spacesInText/2)

        calculatedMin = 30
        if summarySize<calculatedMin:
            calculatedMin=summarySize-1

        # summary is sometimes incomplete sentence, try removing max and min size and see if that helps
        #summary = summarizer(text, max_length=summarySize, min_length=calculatedMin, do_sample=False)
        summary = summarizer(text, do_sample=False)
        summaryLine = summary.pop()['summary_text']
        print(f"Summary:\n\n\n{summaryLine}\n\n")
        summaryLines.append(summaryLine)


# Output the summary

print("\n\n---\n\n")

outputSummary = ""

outputSummary = "\n\n## Key Points\n\n"

for summaryLine in summaryLines:
    # Try summarizing the summary
    spacesInText = summaryLine.count(" ")
    summarySize = int(spacesInText/2)
    calculatedMax = 20
    if summarySize<calculatedMax:
        calculatedMax=summarySize-1

    # Are there any transformers for making a truncated summary valid text?
    # https://www.kdnuggets.com/how-to-summarize-texts-bart-model-hugging-face-transformers
    # https://huggingface.co/transformers/v2.11.0/model_doc/bart.html
    # https://stackoverflow.com/questions/66996270/limiting-bart-huggingface-model-to-complete-sentences-of-maximum-length
    # titleSummary = summarizer(summaryLine, num_beams=10, max_length=calculatedMax, min_length=1, do_sample=False)
    # titleSummaryLine = titleSummary.pop()['summary_text']
    # Try summarizing it again with no limits to get valid sentence? No because then it hallucinates a long text
    # titleSummary = summarizer(titleSummaryLine, do_sample=False)
    # titleSummaryLine = titleSummary.pop()['summary_text']

    # outputSummary = outputSummary + "\n**" + titleSummaryLine + "**\n\n"
    # better to just embolden the first sentence if we do anything at all
    outputSummary = outputSummary + "\n\n" + "* " + summaryLine + "\n\n"

print(outputSummary)

with open(fileToRead + ".summary.2.txt", 'w') as f:
    f.write(outputSummary)